"""
Generation Schemas
Pydantic models for text generation requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProviderEnum(str, Enum):
    """AI Provider enumeration"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"


class ModelEnum(str, Enum):
    """AI Model enumeration"""
    # OpenAI Models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Anthropic Models
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    
    # Google Models
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"


class GenerationRequest(BaseModel):
    """Text generation request"""
    prompt: str = Field(..., min_length=1, max_length=10000)
    provider: ProviderEnum = Field(default=ProviderEnum.OPENAI)
    model: Optional[str] = None
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[List[str]] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GenerationResponse(BaseModel):
    """Text generation response"""
    id: str
    text: str
    provider: str
    model: str
    usage: Dict[str, int]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None


class BatchGenerationRequest(BaseModel):
    """Batch generation request"""
    requests: List[GenerationRequest] = Field(..., min_items=1, max_items=10)
    parallel: bool = Field(default=True)


class BatchGenerationResponse(BaseModel):
    """Batch generation response"""
    results: List[GenerationResponse]
    total_requests: int
    successful: int
    failed: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StreamingGenerationRequest(BaseModel):
    """Streaming generation request"""
    prompt: str = Field(..., min_length=1, max_length=10000)
    provider: ProviderEnum = Field(default=ProviderEnum.OPENAI)
    model: Optional[str] = None
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    stream_chunk_size: int = Field(default=1, ge=1, le=100)


class GenerationHistoryRequest(BaseModel):
    """Generation history request"""
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    provider: Optional[str] = None
    model: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
