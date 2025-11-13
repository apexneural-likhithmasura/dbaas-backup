#!/usr/bin/env python3
"""
Run script for Pain Point & Market Gap Analyzer API

This script starts the FastAPI application with uvicorn.
"""

import uvicorn
from app.core.config import settings


def main():
    """Run the FastAPI application"""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Base URL: {settings.base_url}")
    print(f"API Docs: {settings.base_url}{settings.api_prefix}/docs")
    print("-" * 70)
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug or settings.environment == "development",
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()

