"""
FastAPI application exposing the Reddit Market Opportunity Identifier
workflow via REST endpoints and a WebSocket for realtime progress.
INTEGRATED WITH PAIN POINT EXTRACTOR & MARKET GAP GENERATOR
"""

import os
import sys
import json
import uuid
import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

# Reuse existing modules
from google_search import GoogleSearcher
from reddit_scraper import RedditScraper
from openai_ranker import PostRanker

# Import pain point extractor from parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'painpont-extractor'))
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "json_extraction",
        os.path.join(os.path.dirname(__file__), '..', '..', 'painpont-extractor', 'json-extraction.py')
    )
    json_extraction = importlib.util.module_from_spec(spec)
    sys.modules['json_extraction'] = json_extraction
    spec.loader.exec_module(json_extraction)
    
    from pain_point_extractor import extract_pain_points
    from market_gap_generator import generate_solutions
    PAIN_POINT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Pain point extractor not available: {e}")
    PAIN_POINT_AVAILABLE = False


app = FastAPI(title="Reddit Market Opportunity Identifier API")


# Standard API response helpers and exception handlers
def success_response(message: str, data=None, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content={"message": message, "data": data, "status": "success"}
    )


def error_response(message: str, status_code: int = 400, data=None):
    return JSONResponse(
        status_code=status_code,
        content={"message": message, "data": data, "status": "error"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Request error"
    return error_response(detail, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response("Validation error", status_code=422, data={"errors": exc.errors()})


class StartJobRequest(BaseModel):
    market: str
    num_results: int = 30
    top_n: int = 10
    deep_top_k: int | None = None


class CompletePipelineRequest(BaseModel):
    """Request for complete pipeline: Reddit scraping + Pain point analysis + Market gaps"""
    market: str
    num_results: int = 30
    top_n: int = 10
    deep_top_k: int = 5  # Number of posts to deeply analyze
    ai_model: str = "anthropic/claude-3.5-sonnet"
    temperature: float = 0.7


# In-memory job store
_jobs: dict[str, dict] = {}


# Output configuration (aligned with main.py)
BASE_OUTPUT_DIR = "d:/redditdemo/output"


def _make_market_folder(market: str) -> str:
    safe_market_name = (
        market.replace(' ', '_').replace('"', '').replace('/', '_').replace('\\', '_')
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{safe_market_name}_{timestamp}"
    full_path = os.path.join(BASE_OUTPUT_DIR, folder_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path


def _save_json(dirpath: str, filename: str, data) -> str:
    filename = filename.replace(' ', '_').replace('"', '').replace('/', '_')
    filepath = os.path.join(dirpath, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def _save_text(dirpath: str, filename: str, text: str) -> str:
    filename = filename.replace(' ', '_').replace('"', '').replace('/', '_')
    filepath = os.path.join(dirpath, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    return filepath


async def _run_job(job_id: str, market: str, num_results: int, top_n: int, deep_top_k: int | None):
    job = _jobs[job_id]
    queue: asyncio.Queue = job["queue"]

    def log(message: str):
        queue.put_nowait({"type": "log", "message": message})

    try:
        job["status"] = "running"
        output_dir = _make_market_folder(market)
        job["output_dir"] = output_dir

        # Initialize components (API key via env like main.py)
        api_key = os.getenv("OPENAI_API_KEY")
        searcher = GoogleSearcher()
        scraper = RedditScraper()
        ranker = PostRanker(api_key) if api_key else None

        log(f"STEP 1: Searching Reddit discussions for market: {market}")
        urls = await asyncio.to_thread(searcher.search_market, market, num_results)
        if not urls:
            raise RuntimeError("No Reddit URLs found")

        log(f"STEP 2: Scraping metadata for {len(urls)} posts")
        posts_data = await asyncio.to_thread(scraper.scrape_multiple_posts, urls)
        _save_json(output_dir, f"{market}_raw_posts.json", posts_data)

        log("STEP 3: Ranking posts")
        if ranker is not None:
            ranked_posts = await asyncio.to_thread(ranker.rank_posts, posts_data, market, top_n)
        else:
            # Fallback ranking if API key missing
            ranked_posts = await asyncio.to_thread(PostRanker._fallback_ranking, PostRanker, posts_data, top_n)
        _save_json(output_dir, f"{market}_ranked_posts.json", ranked_posts)

        if ranker is not None:
            formatted = await asyncio.to_thread(ranker.format_ranked_output, ranked_posts, market)
            _save_text(output_dir, f"{market}_ranked_output.txt", formatted)

        log(f"Ranked {len(ranked_posts)} posts")

        deep_analysis = []
        if deep_top_k and deep_top_k > 0:
            k = min(deep_top_k, len(ranked_posts))
            log(f"STEP 4: Deep JSON extraction for top {k} posts")
            for post in ranked_posts[:k]:
                url = post["url"]
                log(f"Fetching JSON: {url}")
                json_data = await asyncio.to_thread(scraper.get_post_json, url)
                if json_data:
                    structured = await asyncio.to_thread(scraper.extract_post_and_comments, json_data)
                    if structured:
                        deep_analysis.append({
                            "rank": post["rank"],
                            "title": post["title"],
                            "url": post["url"],
                            "extracted_data": structured,
                        })
                        _save_json(output_dir, f"{market}_post_rank_{post['rank']}.json", json_data)
                        _save_json(output_dir, f"{market}_post_rank_{post['rank']}_structured.json", structured)

        result = {
            "market": market,
            "total_posts_found": len(urls),
            "ranked_posts": ranked_posts,
            "deep_analysis_count": len(deep_analysis),
            "output_dir": output_dir,
        }
        _save_json(output_dir, f"{market}_complete_analysis.json", result)

        job["result"] = result
        job["status"] = "completed"
        log("WORKFLOW COMPLETE")
        queue.put_nowait({"type": "done"})

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        queue.put_nowait({"type": "error", "message": str(e)})
        queue.put_nowait({"type": "done"})


@app.post("/jobs")
async def start_job(req: StartJobRequest):
    market = req.market.strip()
    if not market:
        raise HTTPException(status_code=400, detail="market is required")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "pending",
        "queue": asyncio.Queue(),
        "result": None,
        "error": None,
        "output_dir": None,
    }

    asyncio.create_task(_run_job(job_id, market, req.num_results, req.top_n, req.deep_top_k))
    return success_response("Job created", {"job_id": job_id})


@app.get("/jobs/{job_id}/status")
async def get_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return success_response("Status fetched", {
        "status": job["status"],
        "error": job["error"],
        "output_dir": job["output_dir"],
    })


@app.get("/jobs/{job_id}/result")
async def get_result(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=425, detail="job not completed")
    return success_response("Result fetched", job["result"])


@app.websocket("/ws/jobs/{job_id}")
async def job_stream(websocket: WebSocket, job_id: str):
    job = _jobs.get(job_id)
    if not job:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "job not found"})
        await websocket.close()
        return

    await websocket.accept()
    queue: asyncio.Queue = job["queue"]

    # If job already finished, emit summary and close
    if job["status"] in ("completed", "failed"):
        if job["error"]:
            await websocket.send_json({"type": "error", "message": job["error"]})
        if job["result"]:
            await websocket.send_json({"type": "result", "data": job["result"]})
        await websocket.close()
        return

    try:
        while True:
            msg = await queue.get()
            await websocket.send_json(msg)
            if msg.get("type") == "done":
                if job["result"]:
                    await websocket.send_json({"type": "result", "data": job["result"]})
                await websocket.close()
                break
    except WebSocketDisconnect:
        return


@app.get("/jobs/{job_id}/files")
async def list_files(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if not job["output_dir"]:
        raise HTTPException(status_code=404, detail="output not available yet")
    files = os.listdir(job["output_dir"])
    return success_response("Files listed", {"files": files})


@app.get("/jobs/{job_id}/files/{name}")
async def download_file(job_id: str, name: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if not job["output_dir"]:
        raise HTTPException(status_code=404, detail="output not available yet")
    path = os.path.join(job["output_dir"], name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path)


# ==================== COMPLETE PIPELINE WITH PAIN POINT ANALYSIS ====================

async def _run_complete_pipeline(
    job_id: str, 
    market: str, 
    num_results: int, 
    top_n: int, 
    deep_top_k: int,
    ai_model: str,
    temperature: float
):
    """Run complete pipeline: Reddit scraping → Pain points → Market gaps"""
    job = _jobs[job_id]
    queue: asyncio.Queue = job["queue"]

    def log(message: str):
        queue.put_nowait({"type": "log", "message": message})

    try:
        if not PAIN_POINT_AVAILABLE:
            raise RuntimeError("Pain point extractor not available")

        job["status"] = "running"
        output_dir = _make_market_folder(market)
        job["output_dir"] = output_dir

        # Initialize components
        api_key = os.getenv("OPENAI_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        searcher = GoogleSearcher()
        scraper = RedditScraper()
        ranker = PostRanker(api_key) if api_key else None

        # STEP 1: Search Reddit
        log(f"STEP 1: Searching Reddit for '{market}'...")
        urls = await asyncio.to_thread(searcher.search_market, market, num_results)
        if not urls:
            raise RuntimeError("No Reddit URLs found")
        log(f"✓ Found {len(urls)} Reddit discussions")

        # STEP 2: Scrape metadata
        log(f"STEP 2: Scraping post metadata...")
        posts_data = await asyncio.to_thread(scraper.scrape_multiple_posts, urls)
        _save_json(output_dir, f"{market}_raw_posts.json", posts_data)
        log(f"✓ Scraped {len(posts_data)} posts")

        # STEP 3: Rank posts
        log("STEP 3: AI ranking posts...")
        if ranker:
            ranked_posts = await asyncio.to_thread(ranker.rank_posts, posts_data, market, top_n)
        else:
            ranked_posts = await asyncio.to_thread(PostRanker._fallback_ranking, PostRanker, posts_data, top_n)
        _save_json(output_dir, f"{market}_ranked_posts.json", ranked_posts)
        log(f"✓ Ranked top {len(ranked_posts)} posts")

        # STEP 4: Deep JSON extraction
        log(f"STEP 4: Deep JSON extraction for top {deep_top_k} posts...")
        json_files = []
        for post in ranked_posts[:deep_top_k]:
            log(f"  Processing: {post['title'][:60]}...")
            json_data = await asyncio.to_thread(scraper.get_post_json, post["url"])
            if json_data:
                # Save raw JSON
                filename = f"{market}_post_rank_{post['rank']}.json"
                filepath = _save_json(output_dir, filename, json_data)
                json_files.append(filepath)
                log(f"  ✓ Saved: {filename}")

        if not json_files:
            raise RuntimeError("No JSON files extracted")
        
        log(f"✓ Extracted {len(json_files)} JSON files")

        # STEP 5: Extract data with json-extraction.py
        log("STEP 5: Processing JSON files with extractor...")
        processed_data = await asyncio.to_thread(
            json_extraction.process_multiple_json_files, 
            json_files
        )
        
        # Save extracted data as JSON
        extracted_json_path = _save_json(
            output_dir, 
            f"{market}_extracted_data.json", 
            processed_data.model_dump()
        )
        log(f"✓ Processed {processed_data.total_posts} posts with {processed_data.total_comments_all} comments")

        # STEP 6: Pain point analysis
        log("STEP 6: Analyzing pain points with AI...")
        pain_points_result = await asyncio.to_thread(
            extract_pain_points,
            file_paths=[extracted_json_path],
            api_key=openrouter_key,
            model=ai_model,
            temperature=temperature,
            input_format="json"
        )

        if pain_points_result["status"] != "success":
            raise RuntimeError(f"Pain point extraction failed: {pain_points_result.get('error')}")
        
        pain_points_data = pain_points_result["data"]
        _save_json(output_dir, f"{market}_pain_points.json", pain_points_data)
        
        # Count pain points
        total_pain_points = sum(
            len(cat.get('pain_points', [])) 
            for cat in pain_points_data.get('categories', [])
        )
        log(f"✓ Identified {total_pain_points} pain points in {len(pain_points_data.get('categories', []))} categories")

        # STEP 7: Market gap generation
        log("STEP 7: Generating market gap solutions...")
        solutions_result = await asyncio.to_thread(
            generate_solutions,
            pain_points_data=pain_points_data,
            api_key=openrouter_key,
            model=ai_model,
            temperature=temperature + 0.1
        )

        if solutions_result["status"] != "success":
            raise RuntimeError(f"Market gap generation failed: {solutions_result.get('error')}")
        
        market_gaps_data = solutions_result["data"]
        _save_json(output_dir, f"{market}_market_gaps.json", market_gaps_data)
        
        # Count solutions
        total_solutions = sum(
            len(fw.get('solutions', [])) 
            for fw in market_gaps_data.get('framework_solutions', [])
        )
        log(f"✓ Generated {total_solutions} solution concepts")

        # STEP 8: Create final result
        result = {
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "reddit_analysis": {
                "total_posts_found": len(urls),
                "posts_ranked": len(ranked_posts),
                "posts_deep_analyzed": len(json_files)
            },
            "pain_point_analysis": {
                "total_pain_points": total_pain_points,
                "categories": len(pain_points_data.get('categories', [])),
                "summary": pain_points_data.get('summary', '')
            },
            "market_gaps": {
                "executive_summary": market_gaps_data.get('executive_summary', ''),
                "total_solutions": total_solutions,
                "frameworks": len(market_gaps_data.get('framework_solutions', [])),
                "top_opportunities": market_gaps_data.get('opportunity_assessment', [])
            },
            "output_dir": output_dir,
            "pain_points": pain_points_data,
            "market_gap_solutions": market_gaps_data,
            "extracted_data": processed_data.model_dump()
        }

        _save_json(output_dir, f"{market}_complete_pipeline_result.json", result)

        job["result"] = result
        job["status"] = "completed"
        log("✅ COMPLETE PIPELINE FINISHED!")
        queue.put_nowait({"type": "done"})

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        log(f"❌ Error: {str(e)}")
        queue.put_nowait({"type": "error", "message": str(e)})
        queue.put_nowait({"type": "done"})


@app.post("/pipeline/complete")
async def start_complete_pipeline(req: CompletePipelineRequest):
    """
    Start complete pipeline: Reddit scraping → Pain point analysis → Market gap generation
    
    Returns job_id to track progress via WebSocket or polling
    """
    if not PAIN_POINT_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Pain point extractor not available. Check installation."
        )

    market = req.market.strip()
    if not market:
        raise HTTPException(status_code=400, detail="market is required")

    # Check for OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        raise HTTPException(
            status_code=400, 
            detail="OPENROUTER_API_KEY not configured in environment"
        )

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "pending",
        "queue": asyncio.Queue(),
        "result": None,
        "error": None,
        "output_dir": None,
    }

    asyncio.create_task(_run_complete_pipeline(
        job_id, 
        market, 
        req.num_results, 
        req.top_n, 
        req.deep_top_k,
        req.ai_model,
        req.temperature
    ))

    return success_response(
        "Complete pipeline job created", 
        {
            "job_id": job_id,
            "market": market,
            "websocket_url": f"/ws/jobs/{job_id}",
            "status_url": f"/jobs/{job_id}/status",
            "result_url": f"/jobs/{job_id}/result"
        }
    )


@app.get("/pipeline/status")
async def pipeline_status():
    """Check if pain point pipeline is available"""
    return success_response(
        "Pipeline status",
        {
            "pain_point_extractor_available": PAIN_POINT_AVAILABLE,
            "openrouter_key_configured": bool(os.getenv("OPENROUTER_API_KEY")),
            "openai_key_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
    )


