"""
Market Idea Expansion Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ...agents.market_idea_expander import MarketIdeaExpanderAgent
from ...core.config import settings
from ...models import request_models

router = APIRouter()


async def generate_market_ideas(request: request_models.MarketIdeaRequest):
    """Generate market ideas based on topic"""
    try:
        agent = MarketIdeaExpanderAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        result = agent.generate(
            topic=request.topic,
            stream=False
        )
        
        return {
            "success": True,
            "message": "Market ideas generated successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market idea generation error: {str(e)}")


async def stream_market_ideas(topic: str = "random ideas"):
    """Stream market ideas generation"""
    try:
        agent = MarketIdeaExpanderAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        async def generate_stream():
            result = agent.generate(topic=topic, stream=True)
            if result.get("status") == "success":
                yield result.get("data", "")
            else:
                yield f"Error: {result.get('error', 'Unknown error')}"
        
        return StreamingResponse(generate_stream(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market idea streaming error: {str(e)}")


# Register routes
router.add_api_route('/generate/', generate_market_ideas, methods=["POST"])
router.add_api_route('/stream/', stream_market_ideas, methods=["GET"])

