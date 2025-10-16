"""
Streaming Routes
Real-time text generation streaming endpoints
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from app.api.controllers.stream_controller import StreamController
from app.api.dependencies import get_current_user, rate_limit
from app.schemas.generation_schema import StreamingGenerationRequest
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/generate")
async def stream_generate_text(
    request: StreamingGenerationRequest,
    current_user=Depends(get_current_user),
    rate_limit_check=Depends(rate_limit)
):
    """Stream text generation in real-time"""
    controller = StreamController()
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        async for chunk in controller.stream_generate_text(
            request=request,
            user=current_user
        ):
            yield f"data: {chunk}\n\n"
        
        # Send completion signal
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.post("/chat")
async def stream_chat(
    request: StreamingGenerationRequest,
    current_user=Depends(get_current_user),
    rate_limit_check=Depends(rate_limit)
):
    """Stream chat-style conversation"""
    controller = StreamController()
    
    async def chat_stream() -> AsyncGenerator[str, None]:
        async for chunk in controller.stream_chat(
            request=request,
            user=current_user
        ):
            yield f"data: {chunk}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        chat_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.post("/completion")
async def stream_completion(
    request: StreamingGenerationRequest,
    current_user=Depends(get_current_user),
    rate_limit_check=Depends(rate_limit)
):
    """Stream text completion"""
    controller = StreamController()
    
    async def completion_stream() -> AsyncGenerator[str, None]:
        async for chunk in controller.stream_completion(
            request=request,
            user=current_user
        ):
            yield f"data: {chunk}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        completion_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )
