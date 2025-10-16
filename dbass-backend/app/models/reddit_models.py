"""
Reddit Research Models

Pydantic models for Reddit scraping, searching, and ranking.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RedditPostMetadata(BaseModel):
    """Model for Reddit post metadata"""
    
    url: str = Field(..., description="Reddit post URL")
    title: str = Field(..., description="Post title")
    upvotes: int = Field(..., description="Number of upvotes", ge=0)
    comment_count: int = Field(..., description="Number of comments", ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.reddit.com/r/AskReddit/comments/abc123/",
                "title": "What's your biggest productivity challenge?",
                "upvotes": 1234,
                "comment_count": 567
            }
        }


class RankedRedditPost(BaseModel):
    """Model for a ranked Reddit post with AI analysis"""
    
    rank: int = Field(..., description="Ranking position", ge=1)
    title: str = Field(..., description="Post title")
    url: str = Field(..., description="Reddit post URL")
    upvotes: int = Field(..., description="Number of upvotes", ge=0)
    comment_count: int = Field(..., description="Number of comments", ge=0)
    justification: str = Field(..., description="AI justification for ranking")
    product_potential_score: int = Field(..., description="Potential score (1-10)", ge=1, le=10)
    
    class Config:
        schema_extra = {
            "example": {
                "rank": 1,
                "title": "Struggling to find time management tools that actually work",
                "url": "https://www.reddit.com/r/productivity/comments/abc123/",
                "upvotes": 2345,
                "comment_count": 432,
                "justification": "Strong pain point with high engagement indicating widespread problem",
                "product_potential_score": 9
            }
        }


class RedditSearchRequest(BaseModel):
    """Request model for Reddit search"""
    
    market: str = Field(
        ...,
        description="Market or topic to search for",
        min_length=2,
        max_length=200,
        example="productivity tools for remote workers"
    )
    
    num_results: int = Field(
        30,
        description="Number of Reddit posts to find",
        ge=5,
        le=100,
        example=30
    )


class RedditScrapeRequest(BaseModel):
    """Request model for scraping Reddit posts"""
    
    urls: List[str] = Field(
        ...,
        description="List of Reddit post URLs to scrape",
        min_items=1,
        max_items=50,
        example=["https://www.reddit.com/r/productivity/comments/abc123/"]
    )


class RedditRankRequest(BaseModel):
    """Request model for ranking Reddit posts"""
    
    posts_data: List[Dict[str, Any]] = Field(
        ...,
        description="List of post metadata to rank",
        min_items=1
    )
    
    market: str = Field(
        ...,
        description="Market context for ranking",
        min_length=2,
        max_length=200,
        example="productivity tools"
    )
    
    top_n: int = Field(
        10,
        description="Number of top posts to return",
        ge=1,
        le=50,
        example=10
    )
    
    model: Optional[str] = Field(
        None,
        description="AI model to use for ranking",
        example="anthropic/claude-3.5-sonnet"
    )


class CompletRedditResearchRequest(BaseModel):
    """Request model for complete Reddit research workflow"""
    
    market: str = Field(
        ...,
        description="Market or topic to research",
        min_length=2,
        max_length=200,
        example="remote work productivity"
    )
    
    num_results: int = Field(
        30,
        description="Number of posts to search for",
        ge=5,
        le=100,
        example=30
    )
    
    top_n: int = Field(
        10,
        description="Number of top posts to rank",
        ge=1,
        le=50,
        example=10
    )
    
    deep_analysis_top_k: int = Field(
        3,
        description="Number of top posts to fully scrape and analyze",
        ge=1,
        le=20,
        example=3
    )
    
    model: Optional[str] = Field(
        None,
        description="AI model to use",
        example="anthropic/claude-3.5-sonnet"
    )


class RedditSearchResponse(BaseModel):
    """Response model for Reddit search"""
    
    message: str = Field(..., description="Response message")
    status: str = Field(..., description="Response status")
    data: Dict[str, Any] = Field(..., description="Search results data")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Found 30 Reddit posts",
                "status": "success",
                "data": {
                    "market": "productivity tools",
                    "total_found": 30,
                    "urls": ["..."]
                }
            }
        }

