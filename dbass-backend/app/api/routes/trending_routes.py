"""
Trending Topics Routes

API endpoint for trending topics functionality.
"""

import logging
from fastapi import APIRouter, HTTPException
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

