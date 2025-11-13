"""
Trending Topics Models

Pydantic models for trending topics data validation and serialization.
"""

import re
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator, HttpUrl


class TrendingTopicBase(BaseModel):
    """Base model for trending topics with validation"""
    
    topic: str = Field(
        ..., 
        min_length=1, 
        max_length=500, 
        description="The trending topic name"
    )
    
    volume: str = Field(
        ..., 
        description="Search volume or popularity metric"
    )
    
    growth: str = Field(
        ..., 
        description="Growth percentage (e.g., +1200%)"
    )
    
    description: str = Field(
        ..., 
        min_length=10, 
        description="Detailed description of the topic"
    )
    
    url: HttpUrl = Field(
        ..., 
        description="Source URL for more information"
    )
    
    time_period: str = Field(
        ..., 
        description="Time period for the trend data"
    )
    
    @validator('growth')
    def validate_growth(cls, v):
        """Validate growth percentage format"""
        if not re.match(r'^\+\d+%$', v):
            raise ValueError('Growth must be in format +XXX% (e.g., +1200%)')
        return v
    
    @validator('volume')
    def validate_volume(cls, v):
        """Validate volume format"""
        if not re.match(r'^[\d\-]+[KM]?$', v):
            raise ValueError('Volume must be a number, range, or number with K/M suffix')
        return v


class TrendingTopic(TrendingTopicBase):
    """Complete trending topic model with ID and timestamps"""
    
    id: int = Field(
        ..., 
        gt=0, 
        description="Unique identifier"
    )
    
    created_at: Optional[datetime] = Field(
        None, 
        description="Record creation timestamp"
    )
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TrendingTopicResponse(BaseModel):
    """Response model for trending topics endpoints"""
    
    status: str = Field(
        ..., 
        description="Response status (success/error)"
    )
    
    message: str = Field(
        ..., 
        description="Response message"
    )
    
    data: List[TrendingTopic] = Field(
        ..., 
        description="List of trending topics"
    )
    
    count: int = Field(
        ..., 
        ge=0, 
        description="Number of items returned"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now, 
        description="Response timestamp"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


