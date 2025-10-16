"""
Prompt Management Routes
CRUD operations for prompt templates and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.api.controllers.prompt_controller import PromptController
from app.api.dependencies import get_current_user, rate_limit
from app.schemas.prompt_schema import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptListResponse,
    PromptCategoryResponse
)
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=PromptResponse)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user=Depends(get_current_user)
):
    """Create a new prompt template"""
    controller = PromptController()
    return await controller.create_prompt(
        prompt_data=prompt_data,
        user=current_user
    )


@router.get("/", response_model=PromptListResponse)
async def list_prompts(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    """List user's prompt templates"""
    controller = PromptController()
    return await controller.list_prompts(
        user=current_user,
        category=category,
        search=search,
        limit=limit,
        offset=offset
    )


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    current_user=Depends(get_current_user)
):
    """Get a specific prompt template"""
    controller = PromptController()
    return await controller.get_prompt(
        prompt_id=prompt_id,
        user=current_user
    )


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    prompt_data: PromptUpdate,
    current_user=Depends(get_current_user)
):
    """Update a prompt template"""
    controller = PromptController()
    return await controller.update_prompt(
        prompt_id=prompt_id,
        prompt_data=prompt_data,
        user=current_user
    )


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    current_user=Depends(get_current_user)
):
    """Delete a prompt template"""
    controller = PromptController()
    return await controller.delete_prompt(
        prompt_id=prompt_id,
        user=current_user
    )


@router.get("/categories/list", response_model=List[PromptCategoryResponse])
async def list_categories(current_user=Depends(get_current_user)):
    """Get list of available prompt categories"""
    controller = PromptController()
    return await controller.list_categories(user=current_user)


@router.post("/{prompt_id}/duplicate", response_model=PromptResponse)
async def duplicate_prompt(
    prompt_id: str,
    current_user=Depends(get_current_user)
):
    """Duplicate an existing prompt template"""
    controller = PromptController()
    return await controller.duplicate_prompt(
        prompt_id=prompt_id,
        user=current_user
    )


@router.post("/{prompt_id}/favorite")
async def toggle_favorite(
    prompt_id: str,
    current_user=Depends(get_current_user)
):
    """Toggle favorite status for a prompt"""
    controller = PromptController()
    return await controller.toggle_favorite(
        prompt_id=prompt_id,
        user=current_user
    )


@router.get("/favorites/list", response_model=PromptListResponse)
async def list_favorite_prompts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    """List user's favorite prompt templates"""
    controller = PromptController()
    return await controller.list_favorite_prompts(
        user=current_user,
        limit=limit,
        offset=offset
    )
