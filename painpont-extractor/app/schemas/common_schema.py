"""
Common Schemas
Shared Pydantic models used across the application
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """Common status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class HealthResponse(BaseModel):
    """Basic health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


class DetailedHealthResponse(BaseModel):
    """Detailed health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database: str = "connected"
    redis: str = "connected"
    services: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: list
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool
