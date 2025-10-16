"""
Reddit Research Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List
import time
from ...reddit_researcher.searcher import RedditSearcher
from ...reddit_researcher.scraper import RedditScraper
from ...reddit_researcher.ranker import RedditRanker
from ...core.config import settings
from ...models import reddit_models

router = APIRouter()


async def search_reddit_posts(request: reddit_models.RedditSearchRequest):
    """Search Reddit posts for a specific market/topic"""
    try:
        searcher = RedditSearcher()
        
        urls = searcher.search_market(
            market_to_explore=request.market,
            num_results=request.num_results or 30
        )
        
        return {
            "success": True,
            "message": f"Found {len(urls)} Reddit posts",
            "data": {
                "market": request.market,
                "urls": urls,
                "count": len(urls)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit search error: {str(e)}")


async def scrape_reddit_posts(request: reddit_models.RedditScrapeRequest):
    """Scrape complete Reddit post data including full content and comments"""
    try:
        scraper = RedditScraper()
        
        # Use the complete scraping functionality from the original code
        posts_data = []
        
        for url in request.urls:
            # Get JSON data first
            json_data = scraper.get_post_json(url)
            if json_data:
                # Extract complete post and comment data
                complete_data = scraper.extract_post_and_comments(json_data)
                if complete_data:
                    posts_data.append(complete_data)
                else:
                    # Fallback to basic metadata if complete extraction fails
                    basic_metadata = scraper.scrape_post_metadata(url)
                    posts_data.append({
                        'post': {
                            'title': basic_metadata['title'],
                            'selftext': 'Content extraction failed',
                            'selftext_html': '',
                            'is_self_post': True,
                            'post_type': 'text',
                            'author': 'unknown',
                            'score': basic_metadata['upvotes'],
                            'upvote_ratio': 0.0,
                            'num_comments': basic_metadata['comment_count'],
                            'created_utc': 0.0,
                            'url': basic_metadata['url'],
                            'permalink': '',
                            'subreddit': 'unknown',
                            'link_flair_text': None,
                            'domain': 'self.unknown',
                            'is_video': False,
                            'thumbnail': 'self',
                            'preview_images': []
                        },
                        'comments': [],
                        'total_comments': 0
                    })
            else:
                # Fallback to basic metadata if JSON fails
                basic_metadata = scraper.scrape_post_metadata(url)
                posts_data.append({
                    'post': {
                        'title': basic_metadata['title'],
                        'selftext': 'Failed to load content',
                        'selftext_html': '',
                        'is_self_post': True,
                        'post_type': 'text',
                        'author': 'unknown',
                        'score': basic_metadata['upvotes'],
                        'upvote_ratio': 0.0,
                        'num_comments': basic_metadata['comment_count'],
                        'created_utc': 0.0,
                        'url': basic_metadata['url'],
                        'permalink': '',
                        'subreddit': 'unknown',
                        'link_flair_text': None,
                        'domain': 'self.unknown',
                        'is_video': False,
                        'thumbnail': 'self',
                        'preview_images': []
                    },
                    'comments': [],
                    'total_comments': 0
                })
            
            # Be polite to Reddit
            time.sleep(1)
        
        return {
            "success": True,
            "message": f"Scraped complete data from {len(posts_data)} Reddit posts",
            "data": {
                "posts": posts_data,
                "count": len(posts_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit scraping error: {str(e)}")


async def scrape_complete_reddit_posts(request: reddit_models.RedditScrapeRequest):
    """Scrape complete Reddit post data including full content and comments"""
    try:
        scraper = RedditScraper()
        
        posts_data = scraper.scrape_multiple_complete_posts(request.urls)
        
        return {
            "success": True,
            "message": f"Scraped complete data from {len(posts_data)} Reddit posts",
            "data": {
                "posts": posts_data,
                "count": len(posts_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete Reddit scraping error: {str(e)}")


async def rank_reddit_posts(request: reddit_models.RedditRankRequest):
    """Rank Reddit posts by market potential using AI"""
    try:
        ranker = RedditRanker(
            api_key=settings.openrouter_api_key,
            model=settings.default_model
        )
        
        ranked_posts = ranker.rank_posts(
            posts_data=request.posts,
            market_to_explore=request.market_context or "",
            top_n=request.top_n or 10
        )
        
        # Extract URLs from ranked posts
        ranked_urls = [post.get('url') for post in ranked_posts if post.get('url')]
        
        return {
            "success": True,
            "message": f"Ranked {len(ranked_posts)} Reddit posts",
            "data": {
                "ranked_urls": ranked_urls,  # URLs in ranked order (most important)
                "ranked_posts": ranked_posts,
                "count": len(ranked_posts)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit ranking error: {str(e)}")


async def complete_reddit_research(request: reddit_models.CompletRedditResearchRequest):
    """Complete Reddit research pipeline: search -> scrape -> rank"""
    try:
        # Step 1: Search
        searcher = RedditSearcher()
        urls = searcher.search_market(
            market_to_explore=request.market,
            num_results=request.num_results or 30
        )
        
        if not urls:
            return {
                "success": False,
                "message": "No Reddit posts found",
                "data": None
            }
        
        # Step 2: Scrape
        scraper = RedditScraper()
        posts_metadata = scraper.scrape_multiple_posts(urls)
        
        if not posts_metadata:
            return {
                "success": False,
                "message": "Failed to scrape Reddit posts",
                "data": None
            }
        
        # Step 3: Rank
        ranker = RedditRanker(
            api_key=settings.openrouter_api_key,
            model=settings.default_model
        )
        
        ranked_posts = ranker.rank_posts(
            posts_data=posts_metadata,
            market_to_explore=request.market,
            top_n=request.top_n or 10
        )
        
        # Extract URLs from ranked posts
        ranked_urls = [post.get('url') for post in ranked_posts if post.get('url')]
        
        return {
            "success": True,
            "message": "Complete Reddit research finished successfully",
            "data": {
                "market": request.market,
                "total_urls_found": len(urls),
                "posts_scraped": len(posts_metadata),
                "posts_ranked": len(ranked_posts),
                "ranked_urls": ranked_urls,  # URLs in ranked order
                "top_posts": ranked_posts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete Reddit research error: {str(e)}")


# Register routes - Only essential endpoints
router.add_api_route('/scrape/', scrape_reddit_posts, methods=["POST"],
                     summary="Scrape Reddit Posts - Get Complete Post Data with Comments")
router.add_api_route('/complete-research/', complete_reddit_research, methods=["POST"],
                     summary="Complete Reddit Research - Search, Scrape & Rank in One Call")
