"""
FastAPI Generative AI Backend Application
Main application entry point with startup configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.error_handler import add_error_handlers
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.request_logger import RequestLoggingMiddleware
from app.db.database import engine, Base
from app.api.routes import (
    health_router,
    generation_router,
    prompt_router,
    stream_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    # Close any open connections, cleanup resources
    pass


# Initialize FastAPI app
app = FastAPI(
    title="Generative AI Backend",
    description="A comprehensive backend for generative AI applications with multiple provider support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimiterMiddleware)

# Add error handlers
add_error_handlers(app)

# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(generation_router, prefix="/api/v1/generation", tags=["Generation"])
app.include_router(prompt_router, prefix="/api/v1/prompts", tags=["Prompts"])
app.include_router(stream_router, prefix="/api/v1/stream", tags=["Streaming"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Generative AI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
