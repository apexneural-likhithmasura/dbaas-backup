"""
Market Gap Generator Agent

This agent generates business solution frameworks based on identified pain points.
It applies multiple strategic frameworks to discover market opportunities.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..models.market_gap_models import (
    SolutionConcept,
    FrameworkSolution,
    OpportunityAssessment,
    MarketGapAnalysis,
    MarketGapResponse
)


logger = logging.getLogger(__name__)


# ==================== Agent Class ====================

class MarketGapGeneratorAgent:
    """
    Agent for generating business solutions based on pain points.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.8
    ):
        """
        Initialize the Market Gap Generator Agent.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default: anthropic/claude-3.5-sonnet)
            base_url: API base URL (default: OpenRouter)
            temperature: Model temperature (default: 0.8)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        
        # Load system prompt from file
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts",
            "market_gap_generator_prompt.txt"
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
        
        logger.info(f"Initialized MarketGapGeneratorAgent with model: {model}")
    
    def generate(
        self,
        pain_points_data: Dict[str, Any],
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate business solutions based on identified pain points.
        
        Args:
            pain_points_data: Dictionary containing pain point analysis
            output_file: Path to save the solution output (optional)
        
        Returns:
            Dictionary with:
                - data: Market gap analysis with solution recommendations
                - status: "success" or "error"
                - error: Error message if status is "error"
                - output_file: Path to saved file if output_file was provided
        """
        start_time = datetime.now()
        logger.info("="*80)
        logger.info("Starting business solution generation")
        logger.info(f"Timestamp: {start_time}")
        logger.info(f"Model: {self.model}")
        logger.info(f"Temperature: {self.temperature}")
        
        try:
            pain_points_text = json.dumps(pain_points_data, indent=2, ensure_ascii=False)
            logger.info(f"Pain points data length: {len(pain_points_text)} characters")
            
            logger.info("Initializing Claude via OpenRouter")
            llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=pain_points_text)
            ]
            
            logger.info("Sending request to Claude for solution generation...")
            response = llm.invoke(messages)
            logger.info("Received solution recommendations from Claude")
            
            solutions_text = response.content.strip()
            logger.info(f"Response length: {len(solutions_text)} characters")
            
            # Clean markdown code blocks if present
            if solutions_text.startswith("```json"):
                solutions_text = solutions_text[7:]
            elif solutions_text.startswith("```"):
                solutions_text = solutions_text[3:]
            
            if solutions_text.endswith("```"):
                solutions_text = solutions_text[:-3]
            
            solutions_text = solutions_text.strip()
            
            # Parse JSON response
            try:
                solutions_json = json.loads(solutions_text)
                logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                # Return text format as fallback
                return {
                    "data": {
                        "executive_summary": solutions_text,
                        "framework_solutions": [],
                        "opportunity_assessment": []
                    },
                    "status": "success"
                }
            
            # Validate with Pydantic model
            try:
                market_gap_analysis = MarketGapAnalysis(**solutions_json)
                logger.info("Successfully validated with Pydantic model")
                validated_data = market_gap_analysis.model_dump()
            except Exception as e:
                logger.warning(f"Pydantic validation failed: {str(e)}, using raw JSON")
                validated_data = solutions_json
            
            result = {
                "data": validated_data,
                "status": "success"
            }
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(validated_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Solutions saved to: {output_file}")
                result["output_file"] = output_file
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Solution generation completed successfully")
            logger.info(f"Total execution time: {execution_time:.2f} seconds")
            logger.info("="*80)
            
            return result
        
        except Exception as e:
            error_msg = str(e)
            logger.error("="*80)
            logger.error(f"Error during solution generation: {error_msg}")
            logger.error("Exception details:", exc_info=True)
            logger.error("="*80)
            
            return {
                "data": "",
                "status": "error",
                "error": error_msg
            }

