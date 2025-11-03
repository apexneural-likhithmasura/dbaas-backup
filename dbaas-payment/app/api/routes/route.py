"""
Main Route File
Imports and combines all route modules
"""

from fastapi import APIRouter
from . import pain_point_routes
from . import market_gap_routes
from . import market_idea_routes
from . import reddit_routes
from . import trending_routes
from . import auth_routes
# Import new unified payments module
from ...payments import routes as payment_routes_new

# Create main router
router = APIRouter()

# Include all sub-routers with prefixes
router.include_router(pain_point_routes.router, prefix="/pain-points", tags=["Pain Points"])
router.include_router(market_gap_routes.router, prefix="/market-gaps", tags=["Market Gaps"])
router.include_router(market_idea_routes.router, prefix="/market-ideas", tags=["Market Ideas"])
router.include_router(reddit_routes.router, prefix="/reddit", tags=["Reddit Research"])
router.include_router(trending_routes.router, prefix="/trending", tags=["Trending Topics"])
router.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
# Use new unified payments routes
router.include_router(payment_routes_new.router, prefix="/payments", tags=["Payments"])
