"""
Main Route File
Imports and combines all route modules
"""

from fastapi import APIRouter
from . import pain_point_routes
from . import market_gap_routes
from . import market_idea_routes
from . import reddit_routes

# Create main router
router = APIRouter()

# Include all sub-routers with prefixes
router.include_router(pain_point_routes.router, prefix="/pain-points", tags=["Pain Points"])
router.include_router(market_gap_routes.router, prefix="/market-gaps", tags=["Market Gaps"])
router.include_router(market_idea_routes.router, prefix="/market-ideas", tags=["Market Ideas"])
router.include_router(reddit_routes.router, prefix="/reddit", tags=["Reddit Research"])
