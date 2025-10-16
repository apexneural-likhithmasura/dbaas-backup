"""
Prompt Schemas
Pydantic models for prompt template management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PromptCategory(str, Enum):
    """Prompt category enumeration"""
    GENERAL = "general"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    BUSINESS = "business"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    MARKETING = "marketing"
    WRITING = "writing"
    CODING = "coding"


class PromptCreate(BaseModel):
    """Create prompt template request"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=50000)
    category: PromptCategory = Field(default=PromptCategory.GENERAL)
    description: Optional[str] = Field(default=None, max_length=1000)
    tags: Optional[List[str]] = Field(default=None, max_items=10)
    variables: Optional[Dict[str, str]] = Field(default=None)
    is_public: bool = Field(default=False)
    metadata: Optional[Dict[str, Any]] = None


class PromptUpdate(BaseModel):
    """Update prompt template request"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=50000)
    category: Optional[PromptCategory] = None
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(None, max_items=10)
    variables: Optional[Dict[str, str]] = None
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class PromptResponse(BaseModel):
    """Prompt template response"""
    id: str
    title: str
    content: str
    category: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    variables: Optional[Dict[str, str]] = None
    is_public: bool
    is_favorite: bool = False
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime
    user_id: str
    metadata: Optional[Dict[str, Any]] = None


class PromptListResponse(BaseModel):
    """Paginated prompt list response"""
    prompts: List[PromptResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class PromptCategoryResponse(BaseModel):
    """Prompt category response"""
    name: str
    display_name: str
    description: str
    count: int
    color: Optional[str] = None


class PromptUsageStats(BaseModel):
    """Prompt usage statistics"""
    prompt_id: str
    total_uses: int
    unique_users: int
    last_used: Optional[datetime] = None
    avg_rating: Optional[float] = None
