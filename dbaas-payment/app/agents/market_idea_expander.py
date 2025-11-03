"""
Market Idea Expander Agent

This agent generates hierarchical market segmentation ideas across Health, Wealth, and Relationships.
It can generate random ideas or focus on specific subcategories.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

from openai import OpenAI


logger = logging.getLogger(__name__)


# ==================== Agent Class ====================

class MarketIdeaExpanderAgent:
    """
    Agent for generating market segmentation ideas and niche exploration.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.7
    ):
        """
        Initialize the Market Idea Expander Agent.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default: anthropic/claude-3.5-sonnet)
            base_url: API base URL (default: OpenRouter)
            temperature: Model temperature (default: 0.7)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        
        # Initialize OpenAI client (compatible with OpenRouter)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Load system prompt from file
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts",
            "market_idea_expander_prompt.txt"
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
        
        logger.info(f"Initialized MarketIdeaExpanderAgent with model: {model}")
    
    def generate(
        self,
        topic: str = "random ideas",
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate market ideas based on topic.
        
        Args:
            topic: Topic to expand on (default: "random ideas")
            stream: Whether to stream the response (default: False)
        
        Returns:
            Dictionary with:
                - data: Generated market ideas as text
                - status: "success" or "error"
                - error: Error message if status is "error"
        """
        logger.info(f"Generating market ideas for topic: {topic}")
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": topic},
            ]
            
            if stream:
                # Return stream object for async handling
                logger.info("Creating streaming response...")
                stream_obj = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    temperature=self.temperature,
                )
                return {
                    "data": stream_obj,
                    "status": "success",
                    "streaming": True
                }
            else:
                # Non-streaming response
                logger.info("Creating non-streaming response...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False,
                    temperature=self.temperature,
                )
                content = response.choices[0].message.content or ""
                
                logger.info(f"Successfully generated {len(content)} characters")
                return {
                    "data": {"text": content},
                    "status": "success",
                    "streaming": False
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during market idea generation: {error_msg}", exc_info=True)
            return {
                "data": {},
                "status": "error",
                "error": error_msg
            }
    
    async def generate_stream(self, topic: str = "random ideas"):
        """
        Generate market ideas with streaming support (async generator).
        
        Args:
            topic: Topic to expand on
        
        Yields:
            Text chunks as they arrive from the API
        """
        logger.info(f"Generating streaming market ideas for topic: {topic}")
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": topic},
            ]
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=self.temperature,
            )
            
            for chunk in stream:
                try:
                    delta = chunk.choices[0].delta
                    text_delta = getattr(delta, "content", None)
                    if text_delta:
                        yield text_delta
                except Exception as e:
                    logger.error(f"Error processing stream chunk: {str(e)}")
                    break
            
            logger.info("Streaming completed successfully")
        
        except Exception as e:
            logger.error(f"Error during streaming: {str(e)}", exc_info=True)
            raise

