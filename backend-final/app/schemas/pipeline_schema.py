"""
Schemas for pipeline requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CompletePipelineRequest(BaseModel):
    """Request model for complete pipeline with Reddit scraping"""
    market: str = Field(..., description="Market/query to search for")
    num_results: int = Field(30, description="Number of Reddit results to fetch")
    top_n: int = Field(10, description="Number of top posts to rank")
    deep_top_k: int = Field(5, description="Number of top posts for deep analysis")
    model: Optional[str] = Field("anthropic/claude-3.5-sonnet", description="AI model to use")
    temperature: Optional[float] = Field(0.7, description="Model temperature")


class TopicRequest(BaseModel):
    """Request model for topic expansion"""
    topic: str = Field(..., description="The topic to expand into market categories")


class RedditPostRequest(BaseModel):
    """Request model for processing Reddit post JSON through pain point extraction and market gap generation"""
    reddit_post: Dict[str, Any] = Field(..., description="The Reddit post data in JSON format")
    model: Optional[str] = Field("anthropic/claude-3.5-sonnet", description="AI model to use")
    temperature: Optional[float] = Field(0.7, description="Model temperature for pain point extraction")
    solution_temperature: Optional[float] = Field(0.8, description="Model temperature for solution generation")


class PromptResponse(BaseModel):
    """Response model for prompt generation"""
    message: str
    status: str
    data: Dict[str, Any]


class RedditSearchRequest(BaseModel):
    """Request model for Reddit search and ranking"""
    market: str = Field(..., description="Market/topic to search for on Reddit")
    num_results: int = Field(30, description="Number of Reddit posts to find")
    top_n: int = Field(10, description="Number of top posts to rank")
    use_ai_ranking: bool = Field(True, description="Use AI for ranking (requires OpenRouter API key)")


class RedditPostUrlsRequest(BaseModel):
    """Request model for scraping specific Reddit post URLs"""
    urls: List[str] = Field(..., description="List of Reddit post URLs to scrape")
    extract_full_json: bool = Field(True, description="Extract full JSON data from posts")

