from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
import json
import importlib.util
import sys
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import json-extraction module (with hyphen in name)
spec = importlib.util.spec_from_file_location(
    "json_extraction", 
    os.path.join(os.path.dirname(__file__), "json-extraction.py")
)
json_extraction = importlib.util.module_from_spec(spec)
sys.modules['json_extraction'] = json_extraction
spec.loader.exec_module(json_extraction)

# Import the extractor and generator functions
from pain_point_extractor import extract_pain_points, PainPointResponse
from market_gap_generator import generate_solutions, MarketGapResponse

# Import Reddit components (if available)
try:
    # Add local reddit folder to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    reddit_path = os.path.join(current_dir, "reddit")
    
    print(f"Looking for Reddit components in: {reddit_path}")
    print(f"Reddit path exists: {os.path.exists(reddit_path)}")
    
    if os.path.exists(reddit_path):
        if reddit_path not in sys.path:
            sys.path.append(reddit_path)
        
        from google_search import GoogleSearcher
        from reddit_scraper import RedditScraper
        from openai_ranker import PostRanker
        
        REDDIT_AVAILABLE = True
        print("✅ Reddit components loaded successfully")
    else:
        raise ImportError(f"Reddit path does not exist: {reddit_path}")
        
except ImportError as e:
    print(f"❌ Reddit components not available: {e}")
    REDDIT_AVAILABLE = False

# Import Market Idea Expander components
from idea_expander.market_idea_expander import SYSTEM_PROMPT as MARKET_EXPANSION_PROMPT, openai_client

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Pain Point & Market Gap Analyzer API",
    description="API to extract pain points from Reddit data and generate business solutions from JSON files",
    version="2.0.0"
)


def _make_market_folder(market: str) -> str:
    """Create a folder for market analysis results"""
    safe_market = "".join(c for c in market if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_market = safe_market.replace(' ', '_')
    output_dir = os.path.join(os.getcwd(), "output", safe_market)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def _save_json(output_dir: str, filename: str, data: Any) -> str:
    """Save data as JSON file"""
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


class CompletePipelineRequest(BaseModel):
    """Request model for complete pipeline with Reddit scraping"""
    market: str = Field(..., description="Market/query to search for")
    num_results: int = Field(30, description="Number of Reddit results to fetch")
    top_n: int = Field(10, description="Number of top posts to rank")
    deep_top_k: int = Field(5, description="Number of top posts for deep analysis")
    model: Optional[str] = Field("anthropic/claude-3.5-sonnet", description="AI model to use")
    temperature: Optional[float] = Field(0.7, description="Model temperature")

class TopicRequest(BaseModel):
    topic: str = Field(..., description="The topic to expand into market categories")

class PromptResponse(BaseModel):
    message: str
    status: str
    data: Dict[str, Any]


async def _run_complete_pipeline(
    market: str, 
    num_results: int, 
    top_n: int, 
    deep_top_k: int,
    ai_model: str,
    temperature: float
):
    """Run complete pipeline: Reddit scraping → Pain points → Market gaps"""
    
    def log(message: str):
        print(message)

    try:
        if not REDDIT_AVAILABLE:
            raise RuntimeError("Reddit components not available. Please ensure reddit-fastapi is properly set up.")

        output_dir = _make_market_folder(market)

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
        
        log("✅ COMPLETE PIPELINE FINISHED!")
        return result

    except Exception as e:
        log(f"❌ Error: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Pain Point & Market Gap Analyzer API",
        "version": "2.0.0",
        "endpoints": {
            "/pipeline/complete": "POST - Complete pipeline: Market query → Reddit → Market Gaps (Recommended)",
            "/generate-prompt": "POST - Generate market expansion prompts only (no Reddit search)",
            "/pipeline/status": "GET - Check system status and AI models",
            "/health": "GET - Health check"
        },
        "features": {
            "ai_powered_expansion": "Claude 3.5 Sonnet",
            "reddit_scraping": "Automated search and analysis",
            "pain_point_extraction": "AI-powered insights",
            "market_gap_generation": "Business solution frameworks"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key)
    }




@app.post("/pipeline/complete")
async def start_complete_pipeline(request: CompletePipelineRequest):
    """
    Run complete pipeline: Reddit scraping → Pain points → Market gaps
    
    Args:
        request: CompletePipelineRequest with market query and parameters
    
    Returns:
        Market gap solutions in JSON format
    """
    if not REDDIT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Reddit components not available. Please ensure reddit-fastapi is properly set up."
        )
    
    try:
        # Run the async pipeline and get result
        result = await _run_complete_pipeline(
            market=request.market,
            num_results=request.num_results,
            top_n=request.top_n,
            deep_top_k=request.deep_top_k,
            ai_model=request.model,
            temperature=request.temperature
        )
        
        # Extract only market gap solutions from the complete result
        market_gaps_data = result.get("market_gap_solutions", {})
        
        return {
            "message": "✅ Complete pipeline finished successfully!",
            "status": "completed",
            "data": market_gaps_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )


@app.get("/pipeline/status")
async def get_pipeline_status():
    """Check if the complete pipeline is available"""
    return {
        "available": REDDIT_AVAILABLE,
        "message": "Complete pipeline with Reddit scraping is available" if REDDIT_AVAILABLE else "Reddit components not available",
        "requirements": {
            "reddit_components": REDDIT_AVAILABLE,
            "openrouter_api_key": bool(os.getenv("OPENROUTER_API_KEY"))
        },
        "ai_models": {
            "market_expansion": "anthropic/claude-3.5-sonnet (via OpenRouter)",
            "pain_point_extraction": "anthropic/claude-3.5-sonnet (via OpenRouter)",
            "market_gap_generation": "anthropic/claude-3.5-sonnet (via OpenRouter)"
        },
        "endpoints": {
            "complete_pipeline": "/pipeline/complete",
            "generate_prompt": "/generate-prompt",
            "topic_to_market_gaps": "/topic-to-market-gaps",
            "status": "/pipeline/status"
        }
    }

@app.post("/generate-prompt", response_model=PromptResponse)
async def generate_prompt(request: TopicRequest):
    """
    Generate market expansion prompt based on user topic.
    This uses OpenAI to expand the topic into market categories, niches, and sub-niches.
    """
    try:
        messages = [
            {"role": "system", "content": MARKET_EXPANSION_PROMPT},
            {"role": "user", "content": request.topic},
        ]
        
        response = openai_client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            messages=messages,
            temperature=0.7,
        )
        
        content = response.choices[0].message.content or ""
        
        return PromptResponse(
            message="Prompt generated successfully",
            status="success",
            data={
                "topic": request.topic,
                "expanded_prompt": content,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating prompt: {str(e)}"
        )

