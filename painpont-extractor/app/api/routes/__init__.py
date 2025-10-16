"""
API Routes Package
Centralized router imports and configuration
"""

from fastapi import APIRouter

# Import all routers
from .health_routes import router as health_router
from .generation_routes import router as generation_router
from .prompt_routes import router as prompt_router
from .stream_routes import router as stream_router

# Export all routers for easy importing
__all__ = [
    "health_router",
    "generation_router", 
    "prompt_router",
    "stream_router"
]

# Optional: Create a main router that combines all routes
main_router = APIRouter()

# Include all sub-routers
main_router.include_router(health_router, prefix="/health", tags=["Health"])
main_router.include_router(generation_router, prefix="/generation", tags=["Generation"])
main_router.include_router(prompt_router, prefix="/prompts", tags=["Prompts"])
main_router.include_router(stream_router, prefix="/stream", tags=["Streaming"])
