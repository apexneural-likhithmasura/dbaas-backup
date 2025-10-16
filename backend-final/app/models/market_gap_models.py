"""
Market Gap Analysis Models

Pydantic models for business solution generation and market gap analysis.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SolutionConcept(BaseModel):
    """Model for a business solution concept addressing market gaps"""
    
    name: str = Field(
        ...,
        description="Clear, descriptive name for the solution",
        min_length=3,
        max_length=100,
        example="Urban Apartment Workspace System"
    )
    
    explanation: str = Field(
        ...,
        description="2-3 sentence explanation of the solution",
        min_length=50,
        max_length=1000,
        example="A modular, wall-mounted workstation designed specifically for apartments under 600 sq ft. Features fold-away components and customizable configurations optimized for minimal footprint."
    )
    
    key_features: List[str] = Field(
        ...,
        description="Key features or components of the solution",
        min_items=2,
        max_items=10,
        example=[
            "Fold-away desk surface",
            "Integrated cable management",
            "Modular storage components",
            "Ergonomic design for standing/sitting"
        ]
    )
    
    value_proposition: str = Field(
        ...,
        description="Primary value proposition for customers",
        min_length=20,
        max_length=500,
        example="The only ergonomic workspace system designed exclusively for micro-apartments, combining professional functionality with space efficiency."
    )
    
    business_model: str = Field(
        ...,
        description="Potential business model description",
        min_length=20,
        max_length=500,
        example="Direct-to-consumer e-commerce with professional installation option. Subscription service for component upgrades and exchanges."
    )
    
    pain_points_addressed: List[str] = Field(
        ...,
        description="Specific pain points this solution addresses",
        min_items=1,
        max_items=10,
        example=[
            "Limited space in urban apartments",
            "High cost of ergonomic furniture",
            "Difficulty finding compact professional setups"
        ]
    )
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Nomad Desk Subscription",
                "explanation": "Monthly subscription service providing high-quality, compact desks with free exchanges. Allows users to upgrade or change styles as their living situation changes.",
                "key_features": [
                    "Monthly desk subscription",
                    "Free upgrades and exchanges",
                    "Professional delivery and setup",
                    "Insurance included"
                ],
                "value_proposition": "Eliminates the risk of investing in furniture that might not fit future spaces.",
                "business_model": "Recurring revenue subscription model with asset utilization optimization",
                "pain_points_addressed": [
                    "Frequent relocations",
                    "Uncertainty about long-term needs",
                    "High upfront costs"
                ]
            }
        }


class FrameworkSolution(BaseModel):
    """Model for solutions generated using a specific strategic framework"""
    
    framework_name: str = Field(
        ...,
        description="Name of the strategic framework used",
        min_length=5,
        max_length=100,
        example="Market Segmentation Framework"
    )
    
    solutions: List[SolutionConcept] = Field(
        ...,
        description="Solution concepts generated from this framework",
        min_items=1,
        max_items=5
    )
    
    class Config:
        schema_extra = {
            "example": {
                "framework_name": "Product Differentiation Framework",
                "solutions": [
                    {
                        "name": "Premium Ergonomic Suite",
                        "explanation": "High-end workspace solution targeting professionals willing to invest in health.",
                        "key_features": ["Premium materials", "Custom ergonomic assessment"],
                        "value_proposition": "Best-in-class ergonomics for health-conscious professionals",
                        "business_model": "Premium pricing with white-glove service",
                        "pain_points_addressed": ["Poor posture", "Back pain"]
                    }
                ]
            }
        }


class OpportunityAssessment(BaseModel):
    """Model for assessing and ranking business opportunities"""
    
    rank: int = Field(
        ...,
        description="Ranking position (1 = best opportunity)",
        ge=1,
        le=10,
        example=1
    )
    
    solution_name: str = Field(
        ...,
        description="Name of the solution being assessed",
        min_length=3,
        max_length=100,
        example="Urban Apartment Workspace System"
    )
    
    market_size_potential: str = Field(
        ...,
        description="Assessment of addressable market size and growth potential",
        min_length=50,
        max_length=1000,
        example="TAM of $2.5B in urban markets with 15% annual growth driven by remote work trends. Target segment of 5M urban professionals."
    )
    
    competitive_advantage: str = Field(
        ...,
        description="Assessment of competitive advantage sustainability",
        min_length=50,
        max_length=1000,
        example="First-mover advantage in micro-apartment segment. Design patents and brand positioning create 2-3 year moat."
    )
    
    implementation_feasibility: str = Field(
        ...,
        description="Assessment of implementation feasibility and requirements",
        min_length=50,
        max_length=1000,
        example="Moderate complexity. Requires furniture design expertise, manufacturing partnerships, and logistics network. 12-18 month MVP timeline."
    )
    
    category_dominance_potential: str = Field(
        ...,
        description="Potential for achieving category leadership",
        min_length=50,
        max_length=1000,
        example="High potential to own 'micro-apartment workspace' category. Strong brand differentiation opportunities and clear positioning."
    )
    
    class Config:
        schema_extra = {
            "example": {
                "rank": 1,
                "solution_name": "Urban Workspace System",
                "market_size_potential": "Large and growing market of 10M+ urban remote workers",
                "competitive_advantage": "Unique focus on space efficiency with ergonomic quality",
                "implementation_feasibility": "Moderate - requires design and manufacturing partnerships",
                "category_dominance_potential": "Strong - opportunity to define new category"
            }
        }


class MarketGapAnalysis(BaseModel):
    """Model for complete market gap analysis with solutions"""
    
    executive_summary: str = Field(
        ...,
        description="Executive overview of market opportunities and solution themes",
        min_length=100,
        max_length=2000,
        example="Analysis reveals significant opportunity in the urban remote work furniture market, particularly for space-efficient ergonomic solutions. Three distinct strategic approaches identified across market segmentation, product differentiation, and business model innovation."
    )
    
    framework_solutions: List[FrameworkSolution] = Field(
        ...,
        description="Solutions organized by strategic framework",
        min_items=1,
        max_items=10
    )
    
    opportunity_assessment: List[OpportunityAssessment] = Field(
        ...,
        description="Top opportunities ranked by potential",
        min_items=1,
        max_items=10
    )
    
    class Config:
        schema_extra = {
            "example": {
                "executive_summary": "Comprehensive analysis of remote work furniture market reveals three high-potential opportunities.",
                "framework_solutions": [
                    {
                        "framework_name": "Market Segmentation Framework",
                        "solutions": []
                    }
                ],
                "opportunity_assessment": [
                    {
                        "rank": 1,
                        "solution_name": "Urban Workspace System",
                        "market_size_potential": "Large market",
                        "competitive_advantage": "Strong differentiation",
                        "implementation_feasibility": "Moderate",
                        "category_dominance_potential": "High"
                    }
                ]
            }
        }


class MarketGapResponse(BaseModel):
    """Model for market gap generation API response"""
    
    data: MarketGapAnalysis = Field(
        ...,
        description="Market gap analysis results"
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
                    "executive_summary": "Market analysis completed successfully",
                    "framework_solutions": [],
                    "opportunity_assessment": []
                },
                "status": "success",
                "error": None
            }
        }

