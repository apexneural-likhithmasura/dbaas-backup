"""
API Request Models

Pydantic models for API request validation.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PainPointExtractionRequest(BaseModel):
    """Request model for pain point extraction from text"""
    
    text_data: str = Field(
        ...,
        description="Text data to analyze (Reddit posts, customer feedback, etc.)",
        min_length=50,
        example="I've been struggling to find a good standing desk that fits in my small apartment. Every desk I find is either too expensive or takes up way too much space. It's really frustrating because I work from home and my back is killing me from sitting at my kitchen counter all day."
    )
    
    model: Optional[str] = Field(
        None,
        description="AI model to use (e.g., 'anthropic/claude-3.5-sonnet')",
        example="anthropic/claude-3.5-sonnet"
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Temperature for AI model (0.0-2.0, higher = more creative)",
        ge=0.0,
        le=2.0,
        example=0.7
    )
    
    class Config:
        schema_extra = {
            "example": {
                "text_data": "I've tried 5 different project management tools and they're all too complicated. I just need something simple to track my tasks without a million features I'll never use.",
                "model": "anthropic/claude-3.5-sonnet",
                "temperature": 0.7
            }
        }


class PainPointFileRequest(BaseModel):
    """Request model for pain point extraction from uploaded files"""
    
    input_format: str = Field(
        "txt",
        description="Input file format: 'txt' or 'json'",
        pattern="^(txt|json)$",
        example="txt"
    )
    
    model: Optional[str] = Field(
        None,
        description="AI model to use",
        example="anthropic/claude-3.5-sonnet"
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Temperature for AI model (0.0-2.0)",
        ge=0.0,
        le=2.0,
        example=0.7
    )
    
    class Config:
        schema_extra = {
            "example": {
                "input_format": "txt",
                "model": "anthropic/claude-3.5-sonnet",
                "temperature": 0.7
            }
        }


class MarketGapRequest(BaseModel):
    """Request model for market gap generation from pain points"""
    
    pain_points_data: Dict[str, Any] = Field(
        ...,
        description="Pain points analysis data (output from pain point extraction)",
        example={
            "summary": "Users struggle with complicated project management tools",
            "categories": [
                {
                    "category_name": "Complexity Issues",
                    "pain_points": [
                        {
                            "heading": "Too Many Features",
                            "summary": "Users overwhelmed by features they don't need",
                            "quotes": ["Too complicated", "Too many options"],
                            "frequency_intensity": "High frequency"
                        }
                    ]
                }
            ],
            "priority_ranking": []
        }
    )
    
    model: Optional[str] = Field(
        None,
        description="AI model to use",
        example="anthropic/claude-3.5-sonnet"
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Temperature for AI model (0.0-2.0, higher recommended for creative solutions)",
        ge=0.0,
        le=2.0,
        example=0.8
    )
    
    class Config:
        schema_extra = {
            "example": {
                "pain_points_data": {
                    "summary": "Analysis complete",
                    "categories": [],
                    "priority_ranking": []
                },
                "model": "anthropic/claude-3.5-sonnet",
                "temperature": 0.8
            }
        }


class MarketIdeaRequest(BaseModel):
    """Request model for market idea expansion"""
    
    topic: str = Field(
        "random ideas",
        description="Topic to expand on (e.g., 'alternative medicine', 'fitness', or 'random ideas' for all markets)",
        min_length=1,
        max_length=200,
        example="alternative medicine"
    )
    
    model: Optional[str] = Field(
        None,
        description="AI model to use",
        example="anthropic/claude-3.5-sonnet"
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Temperature for AI model (0.0-2.0)",
        ge=0.0,
        le=2.0,
        example=0.7
    )
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "fitness for busy professionals",
                "model": "anthropic/claude-3.5-sonnet",
                "temperature": 0.7
            }
        }


class CompletePipelineRequest(BaseModel):
    """Request model for complete analysis pipeline execution"""
    
    text_data: str = Field(
        ...,
        description="Text data to analyze through complete pipeline (pain points → market gaps)",
        min_length=50,
        example="Discussion about challenges in finding healthy meal options for people with dietary restrictions. Many users mention limited choices at restaurants, difficulty meal planning, and high cost of specialized foods."
    )
    
    model: Optional[str] = Field(
        None,
        description="AI model to use for both stages",
        example="anthropic/claude-3.5-sonnet"
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Base temperature for AI model (solution generation will use +0.1)",
        ge=0.0,
        le=2.0,
        example=0.7
    )
    
    class Config:
        schema_extra = {
            "example": {
                "text_data": "Users discussing challenges with remote team collaboration...",
                "model": "anthropic/claude-3.5-sonnet",
                "temperature": 0.7
            }
        }

