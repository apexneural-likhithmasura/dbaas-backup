"""
Trending Topics Routes

API endpoint for trending topics functionality.
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ...services.trending_service import trending_service
from ...models.trending_models import TrendingTopicResponse


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/top-trending",
    response_model=TrendingTopicResponse,
    summary="Get top 6 trending topics",
    description="Retrieve the top 6 trending topics with highest growth percentages"
)
async def get_top_trending():
    """
    Get top 6 trending topics by growth percentage
    
    Returns:
        TrendingTopicResponse with top 6 trending topics
        
    Raises:
        HTTPException: If database table doesn't exist or query fails
    """
    try:
        # Check if table exists
        if not trending_service.check_table_exists():
            logger.error("Trending topics table does not exist")
            raise HTTPException(
                status_code=503, 
                detail="Database table 'trending_topics' does not exist"
            )
        
        # Get top growth topics
        topics = trending_service.get_top_growth_topics(limit=6)
        
        logger.info(f"Successfully retrieved {len(topics)} top trending topics")
        
        return TrendingTopicResponse(
            status="success",
            message=f"Retrieved top {len(topics)} trending topics",
            data=topics,
            count=len(topics)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving top trending topics: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve topics: {str(e)}"
        )


@router.get(
    "/all",
    response_model=TrendingTopicResponse,
    summary="Get all trending topics",
    description="Retrieve all trending topics with optional pagination"
)
async def get_all_trending(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of topics to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Number of topics to skip for pagination")
):
    """
    Get all trending topics with optional pagination
    
    Args:
        limit: Maximum number of topics to return (optional, default: all)
        offset: Number of topics to skip for pagination (default: 0)
    
    Returns:
        TrendingTopicResponse with all trending topics
        
    Raises:
        HTTPException: If database table doesn't exist or query fails
    """
    try:
        # Check if table exists
        if not trending_service.check_table_exists():
            logger.error("Trending topics table does not exist")
            raise HTTPException(
                status_code=503, 
                detail="Database table 'trending_topics' does not exist"
            )
        
        # Get all topics with pagination
        topics = trending_service.get_all_topics(limit=limit, offset=offset)
        
        # Get total count for response
        total_count = trending_service.get_total_count()
        
        logger.info(f"Successfully retrieved {len(topics)} trending topics (offset: {offset}, limit: {limit})")
        
        return TrendingTopicResponse(
            status="success",
            message=f"Retrieved {len(topics)} trending topics" + (f" (showing {offset + 1}-{offset + len(topics)} of {total_count})" if limit else f" (total: {total_count})"),
            data=topics,
            count=len(topics)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving all trending topics: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve topics: {str(e)}"
        )

