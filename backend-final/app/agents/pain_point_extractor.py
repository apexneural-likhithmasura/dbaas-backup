"""
Pain Point Extractor Agent

This agent analyzes Reddit conversations and other text data to extract pain points,
frustrations, and unmet needs using AI.
"""

import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..models.pain_point_models import (
    PainPointItem,
    PainPointCategory,
    PriorityRanking,
    PainPointAnalysis,
    PainPointResponse
)


logger = logging.getLogger(__name__)


# ==================== Agent Class ====================

class PainPointExtractorAgent:
    """
    Agent for extracting pain points from text data using AI.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.7
    ):
        """
        Initialize the Pain Point Extractor Agent.
        
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
        
        # Load system prompt from file
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts",
            "pain_point_extractor_prompt.txt"
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
        
        logger.info(f"Initialized PainPointExtractorAgent with model: {model}")
    
    def _load_txt_file(self, file_path: str) -> str:
        """Load text data from a TXT file."""
        logger.info(f"Loading text file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith('.txt'):
            raise ValueError(f"File must be a .txt file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        logger.info(f"Successfully loaded text file: {len(data)} characters")
        return data
    
    def _load_multiple_txt_files(self, file_paths: List[str]) -> str:
        """Load and combine multiple TXT files."""
        logger.info(f"Loading {len(file_paths)} text files")
        combined_parts = []
        
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Loading file {i}/{len(file_paths)}: {file_path}")
            data = self._load_txt_file(file_path)
            
            # Add separator between files
            combined_parts.append(f"\n{'='*80}")
            combined_parts.append(f"FILE {i}: {os.path.basename(file_path)}")
            combined_parts.append(f"{'='*80}\n")
            combined_parts.append(data)
            combined_parts.append("\n")
        
        combined_text = "\n".join(combined_parts)
        logger.info(f"Successfully combined {len(file_paths)} files: {len(combined_text)} characters")
        return combined_text
    
    def extract(
        self,
        file_paths: List[str],
        input_format: str = "txt"
    ) -> Dict[str, Any]:
        """
        Extract pain points from files.
        
        Args:
            file_paths: List of paths to TXT or JSON files
            input_format: Format of input files - "txt" or "json" (default: "txt")
        
        Returns:
            Dictionary with:
                - data: Structured JSON with pain point analysis
                - status: "success" or "error"
                - error: Error message if status is "error"
        """
        start_time = datetime.now()
        logger.info("="*80)
        logger.info("Starting pain point extraction")
        logger.info(f"Timestamp: {start_time}")
        logger.info(f"Number of files: {len(file_paths)}")
        logger.info(f"Model: {self.model}")
        
        try:
            # Load files based on format
            if input_format == "json":
                logger.info("Loading JSON files...")
                reddit_text = ""
                for file_path in file_paths:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    reddit_text += f"\n{'='*80}\nJSON DATA: {os.path.basename(file_path)}\n{'='*80}\n"
                    reddit_text += json.dumps(json_data, indent=2, ensure_ascii=False) + "\n\n"
                logger.info(f"Successfully loaded {len(file_paths)} JSON file(s)")
            else:
                logger.info("Loading TXT files...")
                reddit_text = self._load_multiple_txt_files(file_paths)
            
            # Initialize LLM
            logger.info(f"Initializing Claude via OpenRouter: {self.model}")
            llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers={
                    "HTTP-Referer": "https://github.com/pain-point-analyzer",
                    "X-Title": "Pain Point Analyzer"
                }
            )
            
            # Create messages
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=reddit_text)
            ]
            
            # Get analysis
            logger.info("Sending request to Claude...")
            response = llm.invoke(messages)
            logger.info("Received response from Claude")
            
            # Parse JSON response
            response_text = response.content.strip()
            
            # Clean markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            analysis_json = json.loads(response_text)
            logger.info("Successfully parsed JSON response")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Completed in {execution_time:.2f} seconds")
            logger.info("=" * 80)
            
            return {
                "data": analysis_json,
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}", exc_info=True)
            return {
                "data": {},
                "status": "error",
                "error": str(e)
            }

