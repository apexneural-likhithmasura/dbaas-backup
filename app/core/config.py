"""
Application configuration settings
"""

import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Pain Point & Market Gap Analyzer API"
    app_version: str = "3.0.0"
    app_description: str = "AI-powered pain point extraction and market gap analysis"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    base_url: str = os.getenv("BASE_URL", "/dbas")
    api_prefix: str = "/api"
    
    # API Keys
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # AI Model Configuration
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-3.5-sonnet"
    default_temperature: float = 0.7
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Database Configuration (for Trending Topics)
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "trending_topics")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_schema: str = os.getenv("DB_SCHEMA", "public")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
