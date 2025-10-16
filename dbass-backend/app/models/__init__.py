"""
Pydantic Models Package

This package contains all Pydantic models for data validation and serialization.
Models are organized by domain for better maintainability.
"""

from .pain_point_models import (
    PainPointItem,
    PainPointCategory,
    PriorityRanking,
    PainPointAnalysis,
    PainPointResponse
)

from .market_gap_models import (
    SolutionConcept,
    FrameworkSolution,
    OpportunityAssessment,
    MarketGapAnalysis,
    MarketGapResponse
)

from .request_models import (
    PainPointExtractionRequest,
    PainPointFileRequest,
    MarketGapRequest,
    MarketIdeaRequest,
    CompletePipelineRequest
)

from .response_models import (
    HealthCheckResponse,
    APIResponse,
    ErrorResponse
)

from .reddit_models import (
    RedditPostMetadata,
    RankedRedditPost,
    RedditSearchRequest,
    RedditScrapeRequest,
    RedditRankRequest,
    CompletRedditResearchRequest,
    RedditSearchResponse
)

__all__ = [
    # Pain Point Models
    "PainPointItem",
    "PainPointCategory",
    "PriorityRanking",
    "PainPointAnalysis",
    "PainPointResponse",
    
    # Market Gap Models
    "SolutionConcept",
    "FrameworkSolution",
    "OpportunityAssessment",
    "MarketGapAnalysis",
    "MarketGapResponse",
    
    # Request Models
    "PainPointExtractionRequest",
    "PainPointFileRequest",
    "MarketGapRequest",
    "MarketIdeaRequest",
    "CompletePipelineRequest",
    
    # Response Models
    "HealthCheckResponse",
    "APIResponse",
    "ErrorResponse",
    
    # Reddit Models
    "RedditPostMetadata",
    "RankedRedditPost",
    "RedditSearchRequest",
    "RedditScrapeRequest",
    "RedditRankRequest",
    "CompletRedditResearchRequest",
    "RedditSearchResponse"
]
