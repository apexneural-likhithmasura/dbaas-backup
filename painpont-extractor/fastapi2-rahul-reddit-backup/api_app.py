"""
FastAPI application exposing the Reddit Market Opportunity Identifier
workflow via REST endpoints and a WebSocket for realtime progress.
"""

import os
import json
import uuid
import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

# Reuse existing modules
from google_search import GoogleSearcher
from reddit_scraper import RedditScraper
from openai_ranker import PostRanker


app = FastAPI(title="Reddit Market Opportunity Identifier API")

# CORS Configuration - Allow frontend to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class QuickSearchRequest(BaseModel):
    query: str
    max_results: int = 10


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
        api_key = os.getenv("OPENROUTER_API_KEY")
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


@app.post("/api/search")
async def quick_search(req: QuickSearchRequest):
    """
    Quick search endpoint for frontend integration.
    Returns Reddit posts without ranking (faster response).
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    
    try:
        # Initialize components
        searcher = GoogleSearcher()
        scraper = RedditScraper()
        
        # Search and scrape
        urls = await asyncio.to_thread(searcher.search_market, query, req.max_results)
        if not urls:
            return success_response("No results found", {"posts": [], "total": 0})
        
        posts_data = await asyncio.to_thread(scraper.scrape_multiple_posts, urls)
        
        # Format posts for frontend
        formatted_posts = []
        for idx, post in enumerate(posts_data, 1):
            formatted_posts.append({
                "id": f"post-{idx}",
                "rank": idx,
                "title": post.get("title", "No title"),
                "url": post.get("url", ""),
                "subreddit": post.get("subreddit", "unknown"),
                "upvotes": post.get("upvotes", 0),
                "comments": post.get("comments", 0),
                "preview": post.get("text_preview", "No preview available")[:300],
                "score": post.get("score", 0),
                "created_utc": post.get("created_utc", ""),
            })
        
        return success_response("Search completed", {
            "posts": formatted_posts,
            "total": len(formatted_posts),
            "query": query
        })
        
    except Exception as e:
        return error_response(f"Search failed: {str(e)}", status_code=500)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return success_response("Reddit API is running")


