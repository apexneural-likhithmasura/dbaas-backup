"""
Pain Point Analysis Models

Pydantic models for pain point extraction and analysis.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PainPointItem(BaseModel):
    """Model for a single pain point identified from user feedback"""
    
    heading: str = Field(
        ...,
        description="Clear descriptive heading for the pain point",
        min_length=1,
        max_length=200,
        example="Difficulty Finding Affordable Ergonomic Furniture"
    )
    
    summary: str = Field(
        ...,
        description="1-2 sentence summary of the pain point",
        min_length=10,
        max_length=500,
        example="Users struggle to find ergonomic desk setups that fit in small apartments while remaining affordable."
    )
    
    quotes: List[str] = Field(
        ...,
        description="Direct user quotes illustrating this pain point",
        min_items=1,
        example=[
            "I've measured every corner of my 450 sq ft apartment and can't find a standing desk that would fit.",
            "Spent $300 on a 'compact' desk that still takes up half my bedroom."
        ]
    )
    
    frequency_intensity: str = Field(
        ...,
        description="Assessment of how frequently this pain point appears and its intensity",
        min_length=10,
        max_length=300,
        example="High frequency (mentioned in ~40% of comments), with intense frustration expressed"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "heading": "Limited Space for Home Office Setup",
                "summary": "Users in small apartments struggle to create functional workspaces without sacrificing living space.",
                "quotes": [
                    "My apartment is so small I have to choose between a desk or a dining table",
                    "Working from my kitchen counter is killing my back"
                ],
                "frequency_intensity": "Very high frequency (60%+ of discussions), strong emotional language used"
            }
        }


class PainPointCategory(BaseModel):
    """Model for a category of related pain points"""
    
    category_name: str = Field(
        ...,
        description="Name of the pain point category",
        min_length=3,
        max_length=100,
        example="Problems with Existing Solutions"
    )
    
    pain_points: List[PainPointItem] = Field(
        ...,
        description="List of pain points in this category",
        min_items=1
    )
    
    class Config:
        schema_extra = {
            "example": {
                "category_name": "Product Quality Issues",
                "pain_points": [
                    {
                        "heading": "Poor Build Quality",
                        "summary": "Users report furniture breaking within months of purchase.",
                        "quotes": ["My desk wobbles constantly", "Chair armrest snapped after 3 months"],
                        "frequency_intensity": "High frequency, moderate intensity"
                    }
                ]
            }
        }


class PriorityRanking(BaseModel):
    """Model for priority ranking of pain points based on multiple criteria"""
    
    rank: int = Field(
        ...,
        description="Ranking position (1 = highest priority)",
        ge=1,
        example=1
    )
    
    pain_point: str = Field(
        ...,
        description="Pain point description",
        min_length=10,
        max_length=500,
        example="Lack of affordable ergonomic solutions for small spaces"
    )
    
    frequency: str = Field(
        ...,
        description="How often this pain point appears",
        pattern="^(high|medium|low)$",
        example="high"
    )
    
    intensity: str = Field(
        ...,
        description="Emotional intensity of user frustration",
        pattern="^(high|medium|low)$",
        example="high"
    )
    
    specificity: str = Field(
        ...,
        description="How specific and actionable the pain point is",
        pattern="^(high|medium|low)$",
        example="high"
    )
    
    solvability: str = Field(
        ...,
        description="Feasibility of solving this pain point",
        pattern="^(high|medium|low)$",
        example="medium"
    )
    
    reasoning: str = Field(
        ...,
        description="Brief explanation of ranking rationale",
        min_length=20,
        max_length=500,
        example="This pain point appears in 60% of discussions with strong emotional language, is highly specific, and represents a clear market gap."
    )
    
    class Config:
        schema_extra = {
            "example": {
                "rank": 1,
                "pain_point": "Expensive ergonomic furniture designed only for large spaces",
                "frequency": "high",
                "intensity": "high",
                "specificity": "high",
                "solvability": "medium",
                "reasoning": "Affects majority of urban remote workers, strong willingness to pay, clear solution path exists"
            }
        }


class PainPointAnalysis(BaseModel):
    """Model for complete pain point analysis results"""
    
    summary: str = Field(
        ...,
        description="Executive summary of major pain points identified",
        min_length=50,
        max_length=1000,
        example="Analysis of 150 Reddit discussions revealed three major pain point categories affecting remote workers in urban environments."
    )
    
    categories: List[PainPointCategory] = Field(
        ...,
        description="Categorized pain points organized by theme",
        min_items=1
    )
    
    priority_ranking: List[PriorityRanking] = Field(
        ...,
        description="Priority ranked pain points based on multiple criteria",
        min_items=1
    )
    
    class Config:
        schema_extra = {
            "example": {
                "summary": "Analysis identified 15 distinct pain points across 3 categories, affecting primarily urban professionals aged 25-40.",
                "categories": [
                    {
                        "category_name": "Space Constraints",
                        "pain_points": []
                    }
                ],
                "priority_ranking": [
                    {
                        "rank": 1,
                        "pain_point": "Lack of compact ergonomic furniture",
                        "frequency": "high",
                        "intensity": "high",
                        "specificity": "high",
                        "solvability": "medium",
                        "reasoning": "Most frequently mentioned with strong emotional language"
                    }
                ]
            }
        }


class PainPointResponse(BaseModel):
    """Model for pain point extraction API response"""
    
    data: PainPointAnalysis = Field(
        ...,
        description="Pain point analysis results"
    )
    
    status: str = Field(
        ...,
        description="Response status",
        pattern="^(success|error)$",
        example="success"
    )
    
    error: Optional[str] = Field(
        None,
        description="Error message if status is 'error'",
        example=None
    )
    
    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "summary": "Comprehensive pain point analysis completed",
                    "categories": [],
                    "priority_ranking": []
                },
                "status": "success",
                "error": None
            }
        }

