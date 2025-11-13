"""
Pain Point & Market Gap Analyzer API - Main Application

This is the main entry point for the FastAPI application.
It imports and integrates all components from the existing codebase.
"""

import logging
import os
import sys
import importlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logging import setup_logging
from .api.routes.route import router as api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Add parent directory to path to import existing modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=None,  # We'll set these manually with base_url
    redoc_url=None,
    openapi_url=None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include API router with base_url and api_prefix
app.include_router(api_router, prefix=f"{settings.base_url}{settings.api_prefix}")

# Mount docs at the correct paths
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

@app.get(f"{settings.base_url}{settings.api_prefix}/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        routes=app.routes
    )

@app.get(f"{settings.base_url}{settings.api_prefix}/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(
        openapi_url=f"{settings.base_url}{settings.api_prefix}/openapi.json",
        title=settings.app_name
    )

@app.get(f"{settings.base_url}{settings.api_prefix}/redoc", include_in_schema=False)
async def get_redoc_documentation():
    return get_redoc_html(
        openapi_url=f"{settings.base_url}{settings.api_prefix}/openapi.json",
        title=settings.app_name
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Base URL: {settings.base_url}")
    logger.info(f"API Prefix: {settings.api_prefix}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"CORS Origins: {settings.cors_origins}")
    
    # Check for OpenRouter API key
    if not settings.openrouter_api_key:
        logger.warning("OPENROUTER_API_KEY not set. Some features may not work.")
    else:
        logger.info("OpenRouter API key configured")
    
    logger.info(f"API Documentation: {settings.base_url}{settings.api_prefix}/docs")
    logger.info("Application startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down application...")
    logger.info("Application shutdown complete")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

