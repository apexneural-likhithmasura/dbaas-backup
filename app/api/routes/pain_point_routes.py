"""
Pain Point Extraction Routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional, Dict, Any
import tempfile
import os
import json
from ...agents.pain_point_extractor import PainPointExtractorAgent
from ...agents.market_gap_generator import MarketGapGeneratorAgent
from ...core.config import settings
from ...models import request_models
# Note: We don't need to import the json_extraction functions since we handle
# JSON processing inline in the routes using the PainPointExtractorAgent directly

router = APIRouter()


async def extract_pain_points_text(request: request_models.PainPointExtractionRequest):
    """Extract pain points from text data"""
    try:
        agent = PainPointExtractorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        # Create a temporary text file with the provided text
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tf:
            tf.write(request.text_data)
            temp_file = tf.name
        
        try:
            result = agent.extract(file_paths=[temp_file], input_format="txt")
        finally:
            # Cleanup temp file
            os.unlink(temp_file)
        
        return {
            "success": True,
            "message": "Pain points extracted successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pain point extraction error: {str(e)}")


async def extract_pain_points_from_json_data(json_data: Dict[str, Any]):
    """Extract pain points from JSON data (Reddit post/comment structure)"""
    try:
        agent = PainPointExtractorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tf:
            json.dump(json_data, tf, indent=2, ensure_ascii=False)
            temp_file = tf.name
        
        try:
            result = agent.extract(file_paths=[temp_file], input_format="json")
        finally:
            # Cleanup temp file
            os.unlink(temp_file)
        
        return {
            "success": True,
            "message": "Pain points extracted from JSON data successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON pain point extraction error: {str(e)}")


async def extract_pain_points_file(files: List[UploadFile] = File(...)):
    """Extract pain points from uploaded files (JSON or TXT)"""
    temp_files = []
    try:
        # Save uploaded files temporarily and determine format
        file_formats = []
        for file in files:
            suffix = os.path.splitext(file.filename)[1].lower()
            if suffix == '.json':
                file_formats.append('json')
            else:
                file_formats.append('txt')
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix) as tf:
                content = await file.read()
                tf.write(content.decode('utf-8'))
                temp_files.append(tf.name)
        
        agent = PainPointExtractorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        # Determine input format (use JSON if any file is JSON)
        input_format = "json" if any(fmt == 'json' for fmt in file_formats) else "txt"
        
        # Extract pain points from files
        result = agent.extract(file_paths=temp_files, input_format=input_format)
        
        return {
            "success": True,
            "message": f"Pain points extracted from {len(files)} files successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File pain point extraction error: {str(e)}")
    finally:
        # Cleanup temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


async def extract_pain_points_from_reddit_data(reddit_data: Dict[str, Any]):
    """
    Extract pain points from Reddit post/comment data structure.
    Accepts the same format as returned by /reddit/scrape-complete/ endpoint.
    """
    try:
        agent = PainPointExtractorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        # Create temporary JSON file with the Reddit data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tf:
            json.dump(reddit_data, tf, indent=2, ensure_ascii=False)
            temp_file = tf.name
        
        try:
            result = agent.extract(file_paths=[temp_file], input_format="json")
        finally:
            # Cleanup temp file
            os.unlink(temp_file)
        
        return {
            "success": True,
            "message": "Pain points extracted from Reddit data successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit pain point extraction error: {str(e)}")


async def complete_analysis_pipeline_text(request: request_models.PainPointExtractionRequest):
    """
    Complete pipeline: Extract pain points from text data and generate market gaps.
    Returns both pain points and market gap solutions.
    """
    try:
        # Step 1: Extract pain points
        pain_point_agent = PainPointExtractorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        # Create a temporary text file with the provided text
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tf:
            tf.write(request.text_data)
            temp_file = tf.name
        
        try:
            pain_points_result = pain_point_agent.extract(file_paths=[temp_file], input_format="txt")
        finally:
            # Cleanup temp file
            os.unlink(temp_file)
        
        # Check if pain point extraction was successful
        if pain_points_result.get("status") != "success":
            raise HTTPException(
                status_code=500, 
                detail=f"Pain point extraction failed: {pain_points_result.get('error', 'Unknown error')}"
            )
        
        # Step 2: Generate market gaps from pain points
        market_gap_agent = MarketGapGeneratorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=0.8  # Higher temperature for creative market gap generation
        )
        
        market_gaps_result = market_gap_agent.generate(
            pain_points_data=pain_points_result.get("data")
        )
        
        # Check if market gap generation was successful
        if market_gaps_result.get("status") != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Market gap generation failed: {market_gaps_result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": "Complete analysis pipeline executed successfully",
            "data": {
                "pain_points": pain_points_result.get("data"),
                "market_gaps": market_gaps_result.get("data")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


async def complete_analysis_pipeline_file(files: List[UploadFile] = File(...)):
    """
    Complete pipeline: Extract pain points from uploaded files and generate market gaps.
    Returns both pain points and market gap solutions.
    """
    temp_files = []
    try:
        # Save uploaded files temporarily and determine format
        file_formats = []
        for file in files:
            suffix = os.path.splitext(file.filename)[1].lower()
            if suffix == '.json':
                file_formats.append('json')
            else:
                file_formats.append('txt')
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix) as tf:
                content = await file.read()
                tf.write(content.decode('utf-8'))
                temp_files.append(tf.name)
        
        # Step 1: Extract pain points
        pain_point_agent = PainPointExtractorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        # Determine input format (use JSON if any file is JSON)
        input_format = "json" if any(fmt == 'json' for fmt in file_formats) else "txt"
        
        # Extract pain points from files
        pain_points_result = pain_point_agent.extract(file_paths=temp_files, input_format=input_format)
        
        # Check if pain point extraction was successful
        if pain_points_result.get("status") != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Pain point extraction failed: {pain_points_result.get('error', 'Unknown error')}"
            )
        
        # Step 2: Generate market gaps from pain points
        market_gap_agent = MarketGapGeneratorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=0.8
        )
        
        market_gaps_result = market_gap_agent.generate(
            pain_points_data=pain_points_result.get("data")
        )
        
        # Check if market gap generation was successful
        if market_gaps_result.get("status") != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Market gap generation failed: {market_gaps_result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": f"Complete analysis pipeline executed successfully for {len(files)} files",
            "data": {
                "pain_points": pain_points_result.get("data"),
                "market_gaps": market_gaps_result.get("data")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    finally:
        # Cleanup temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


async def complete_analysis_pipeline_reddit(reddit_data: Dict[str, Any]):
    """
    Complete pipeline: Extract pain points from Reddit data and generate market gaps.
    
    Accepts multiple input formats:
    1. Single post: {"post": {...}, "comments": [...], "total_comments": N}
    2. Multiple posts: {"posts": [{...}, {...}]}
    3. Scraped data: {"data": {"posts": [...]}}
    
    Returns both pain points and market gap solutions.
    """
    try:
        # Normalize input format - handle different structures
        normalized_data = reddit_data
        
        # If data is wrapped in "data" key, unwrap it
        if "data" in reddit_data and "posts" in reddit_data["data"]:
            # Format: {"data": {"posts": [...]}}
            normalized_data = reddit_data["data"]["posts"][0] if reddit_data["data"]["posts"] else reddit_data
        elif "posts" in reddit_data and isinstance(reddit_data["posts"], list):
            # Format: {"posts": [{...}, {...}]}
            normalized_data = reddit_data["posts"][0] if reddit_data["posts"] else reddit_data
        
        # Validate we have the required structure
        if "post" not in normalized_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid input format. Expected format: {'post': {...}, 'comments': [...]}"
            )
        
        # Step 1: Extract pain points
        pain_point_agent = PainPointExtractorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.default_temperature
        )
        
        # Create temporary JSON file with the normalized Reddit data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tf:
            json.dump(normalized_data, tf, indent=2, ensure_ascii=False)
            temp_file = tf.name
        
        try:
            pain_points_result = pain_point_agent.extract(file_paths=[temp_file], input_format="json")
        finally:
            # Cleanup temp file
            os.unlink(temp_file)
        
        # Check if pain point extraction was successful
        if pain_points_result.get("status") != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Pain point extraction failed: {pain_points_result.get('error', 'Unknown error')}"
            )
        
        # Step 2: Generate market gaps from pain points
        market_gap_agent = MarketGapGeneratorAgent(
            api_key=settings.openrouter_api_key,
            model=settings.default_model,
            base_url=settings.openrouter_base_url,
            temperature=0.8
        )
        
        market_gaps_result = market_gap_agent.generate(
            pain_points_data=pain_points_result.get("data")
        )
        
        # Check if market gap generation was successful
        if market_gaps_result.get("status") != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Market gap generation failed: {market_gaps_result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": "Complete analysis pipeline executed successfully from Reddit data",
            "data": {
                "pain_points": pain_points_result.get("data"),
                "market_gaps": market_gaps_result.get("data")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


# Register routes - Only essential combined endpoints
# Complete pipeline routes (pain points + market gaps)
router.add_api_route('/complete-analysis-file/', complete_analysis_pipeline_file, methods=["POST"],
                     summary="Complete Analysis: Extract Pain Points & Generate Market Gaps from File (JSON/TXT)")
router.add_api_route('/complete-analysis-reddit/', complete_analysis_pipeline_reddit, methods=["POST"],
                     summary="Complete Analysis: Extract Pain Points & Generate Market Gaps from Reddit Data")
