"""
API Response Models

Pydantic models for standardized API responses.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(
        ...,
        description="Health status",
        pattern="^(healthy|degraded|unhealthy)$",
        example="healthy"
    )
    
    timestamp: str = Field(
        ...,
        description="ISO timestamp of health check",
        example="2025-10-15T10:30:00Z"
    )
    
    version: str = Field(
        ...,
        description="API version",
        example="3.0.0"
    )
    
    configuration: Dict[str, Any] = Field(
        ...,
        description="Configuration status",
        example={
            "openrouter_api_key": "configured",
            "default_model": "anthropic/claude-3.5-sonnet",
            "debug_mode": False
        }
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-15T10:30:00Z",
                "version": "3.0.0",
                "configuration": {
                    "openrouter_api_key": "configured",
                    "default_model": "anthropic/claude-3.5-sonnet",
                    "debug_mode": False
                }
            }
        }


class APIResponse(BaseModel):
    """Generic API response model"""
    
    message: str = Field(
        ...,
        description="Response message",
        example="Operation completed successfully"
    )
    
    status: str = Field(
        ...,
        description="Response status",
        pattern="^(success|error|processing)$",
        example="success"
    )
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Response data payload",
        example={"result": "data"}
    )
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Pain points extracted successfully",
                "status": "success",
                "data": {
                    "summary": "Analysis complete",
                    "categories": []
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    
    message: str = Field(
        ...,
        description="Error message",
        example="An error occurred"
    )
    
    status: str = Field(
        "error",
        description="Always 'error' for error responses",
        pattern="^error$",
        example="error"
    )
    
    error: str = Field(
        ...,
        description="Detailed error description",
        example="Invalid input format"
    )
    
    error_code: Optional[str] = Field(
        None,
        description="Error code for programmatic handling",
        example="INVALID_INPUT"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
        example={"field": "text_data", "issue": "too short"}
    )
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Validation error",
                "status": "error",
                "error": "Input text must be at least 50 characters",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "field": "text_data",
                    "min_length": 50,
                    "provided_length": 20
                }
            }
        }


class EndpointInfo(BaseModel):
    """Model for endpoint information"""
    
    path: str = Field(..., description="Endpoint path", example="/agents/pain-points/extract-text")
    method: str = Field(..., description="HTTP method", example="POST")
    description: str = Field(..., description="Endpoint description", example="Extract pain points from text")
    
    class Config:
        schema_extra = {
            "example": {
                "path": "/agents/pain-points/extract-text",
                "method": "POST",
                "description": "Extract pain points from provided text data"
            }
        }


class RootResponse(BaseModel):
    """Response model for root endpoint"""
    
    message: str = Field(..., description="Welcome message")
    version: str = Field(..., description="API version")
    status: str = Field(..., description="Operational status")
    endpoints: Dict[str, Any] = Field(..., description="Available endpoints")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Pain Point & Market Gap Analyzer API",
                "version": "3.0.0",
                "status": "operational",
                "endpoints": {
                    "health": "/health",
                    "pain_points": {},
                    "market_gaps": {},
                    "market_ideas": {}
                }
            }
        }

