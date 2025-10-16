"""
Text Generation Routes
AI text generation endpoints for various providers
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from app.api.controllers.generation_controller import GenerationController
from app.api.dependencies import get_current_user, rate_limit
from app.schemas.generation_schema import (
    GenerationRequest,
    GenerationResponse,
    BatchGenerationRequest,
    BatchGenerationResponse,
    GenerationHistoryRequest
)
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    rate_limit_check=Depends(rate_limit)
):
    """Generate text using specified AI provider"""
    controller = GenerationController()
    return await controller.generate_text(
        request=request,
        user=current_user,
        background_tasks=background_tasks
    )


@router.post("/generate/batch", response_model=BatchGenerationResponse)
async def generate_text_batch(
    request: BatchGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    rate_limit_check=Depends(rate_limit)
):
    """Generate multiple texts in batch"""
    controller = GenerationController()
    return await controller.generate_text_batch(
        request=request,
        user=current_user,
        background_tasks=background_tasks
    )


@router.get("/history", response_model=List[GenerationResponse])
async def get_generation_history(
    limit: int = 50,
    offset: int = 0,
    provider: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """Get user's generation history"""
    controller = GenerationController()
    return await controller.get_generation_history(
        user=current_user,
        limit=limit,
        offset=offset,
        provider=provider
    )


@router.get("/history/{generation_id}", response_model=GenerationResponse)
async def get_generation_by_id(
    generation_id: str,
    current_user=Depends(get_current_user)
):
    """Get specific generation by ID"""
    controller = GenerationController()
    return await controller.get_generation_by_id(
        generation_id=generation_id,
        user=current_user
    )


@router.delete("/history/{generation_id}")
async def delete_generation(
    generation_id: str,
    current_user=Depends(get_current_user)
):
    """Delete a generation record"""
    controller = GenerationController()
    return await controller.delete_generation(
        generation_id=generation_id,
        user=current_user
    )


@router.get("/providers")
async def get_available_providers():
    """Get list of available AI providers"""
    controller = GenerationController()
    return await controller.get_available_providers()


@router.get("/models/{provider}")
async def get_provider_models(provider: str):
    """Get available models for a specific provider"""
    controller = GenerationController()
    return await controller.get_provider_models(provider=provider)
