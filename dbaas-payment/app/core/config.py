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
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Reddit Configuration (Optional)
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "")
    
    # Google Search Configuration (Optional)
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_cse_id: str = os.getenv("GOOGLE_CSE_ID", "")
    
    # AI Model Configuration
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-3.5-sonnet"
    default_temperature: float = 0.7
    
    # Logging
    log_level: str = "INFO"
    log_file: str = os.getenv("LOG_FILE", "")
    
    # CORS
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    cors_methods: str = os.getenv("CORS_METHODS", "*")
    cors_headers: str = os.getenv("CORS_HEADERS", "*")
    
    # Payments / Providers
    payment_provider: str = os.getenv("PAYMENT_PROVIDER", "paypal")
    
    # PayPal
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    paypal_env: str = os.getenv("PAYPAL_ENV", "sandbox")
    paypal_webhook_id: str = os.getenv("PAYPAL_WEBHOOK_ID", "")
    
    # Razorpay
    razorpay_key_id: str = os.getenv("RAZORPAY_KEY_ID", "")
    razorpay_key_secret: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    razorpay_webhook_secret: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    
    # File storage for payments (for testing without DB)
    payments_data_dir: str = os.getenv("PAYMENTS_DATA_DIR", "./data")
    payments_currency: str = os.getenv("PAYMENTS_CURRENCY", "USD")

    # PayPal redirect URLs
    paypal_return_url: str = os.getenv("PAYPAL_RETURN_URL", "")
    paypal_cancel_url: str = os.getenv("PAYPAL_CANCEL_URL", "")
    paypal_success_redirect: str = os.getenv("PAYPAL_SUCCESS_REDIRECT", "")
    paypal_failure_redirect: str = os.getenv("PAYPAL_FAILURE_REDIRECT", "")
    
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
