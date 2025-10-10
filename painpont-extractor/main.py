from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
import json
import importlib.util
import sys
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import json-extraction module (with hyphen in name)
spec = importlib.util.spec_from_file_location(
    "json_extraction", 
    os.path.join(os.path.dirname(__file__), "json-extraction.py")
)
json_extraction = importlib.util.module_from_spec(spec)
sys.modules['json_extraction'] = json_extraction
spec.loader.exec_module(json_extraction)

# Import the extractor and generator functions
from pain_point_extractor import extract_pain_points, PainPointResponse
from market_gap_generator import generate_solutions, MarketGapResponse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Pain Point & Market Gap Analyzer API",
    description="API to extract pain points from Reddit data and generate business solutions from JSON files",
    version="2.0.0"
)


class PipelineResponse(BaseModel):
    """Complete pipeline response model"""
    market_gap_solutions: Dict[str, Any] = Field(..., description="Market gap solutions with structured data")
    pain_points: Dict[str, Any] = Field(..., description="Extracted pain points")
    total_posts: int = Field(..., description="Number of posts processed")
    total_comments: int = Field(..., description="Total comments analyzed")
    files_processed: List[str] = Field(..., description="List of processed files")
    status: str = Field(..., description="Pipeline status")
    message: Optional[str] = Field(None, description="Additional message")


class JSONFilePathRequest(BaseModel):
    """Request model for analyzing existing JSON files"""
    file_paths: List[str] = Field(..., description="List of JSON file paths")
    model: Optional[str] = Field("anthropic/claude-3.5-sonnet", description="AI model to use")
    temperature: Optional[float] = Field(0.7, description="Model temperature")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Pain Point & Market Gap Analyzer API",
        "version": "2.0.0",
        "endpoints": {
            "/analyze-json-files": "POST - Upload JSON files for analysis",
            "/analyze-json-paths": "POST - Analyze JSON files from existing paths",
            "/health": "GET - Health check"
        },
        "features": {
            "multi_file_support": True,
            "json_formats": ["simple", "reddit_api"],
            "pipeline_stages": ["json_extraction", "pain_points", "market_gaps"]
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key)
    }


@app.post("/analyze-json-files", response_model=PipelineResponse)
async def analyze_uploaded_json_files(
    files: List[UploadFile] = File(...),
    model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.7
):
    """
    Analyze uploaded JSON files through complete pipeline:
    JSON → Extract Data (Pydantic) → Convert to JSON → Pain Points (AI) → Market Gaps (AI) → JSON Response
    
    Args:
        files: List of JSON files containing Reddit posts/comments
        model: AI model to use (default: anthropic/claude-3.5-sonnet)
        temperature: Model temperature (default: 0.7)
    
    Returns:
        JSON response with market gap solutions and pain points analysis
    """
    temp_dir = None
    
    try:
        # Validate files
        for file in files:
            if not file.filename.endswith('.json'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a JSON file. Only .json files are accepted."
                )
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        json_file_paths = []
        
        # Save uploaded JSON files
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            json_file_paths.append(file_path)
        
        # Step 1: Extract data from JSON files
        processed_data = json_extraction.process_multiple_json_files(json_file_paths)
        
        # Step 2: Save extracted data as JSON
        extracted_json_path = os.path.join(temp_dir, "extracted_data.json")
        with open(extracted_json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data.model_dump(), f, indent=2, ensure_ascii=False)
        
        # Step 3: Extract pain points from JSON data directly
        pain_points_result = extract_pain_points(
            file_paths=[extracted_json_path],
            model=model,
            temperature=temperature,
            input_format="json"
        )
        
        if pain_points_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Pain point extraction failed: {pain_points_result.get('error', 'Unknown error')}"
            )
        
        # Step 4: Generate market gap solutions
        solutions_result = generate_solutions(
            pain_points_data=pain_points_result["data"],
            model=model,
            temperature=temperature + 0.1
        )
        
        if solutions_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Solution generation failed: {solutions_result.get('error', 'Unknown error')}"
            )
        
        # Return structured response
        return PipelineResponse(
            market_gap_solutions=solutions_result["data"],
            pain_points=pain_points_result["data"],
            total_posts=processed_data.total_posts,
            total_comments=processed_data.total_comments_all,
            files_processed=[os.path.basename(f) for f in json_file_paths],
            status="success",
            message=f"Successfully processed {len(files)} JSON file(s)"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}"
        )
    
    finally:
        # Cleanup temporary files
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.post("/analyze-json-paths", response_model=PipelineResponse)
async def analyze_json_file_paths(request: JSONFilePathRequest):
    """
    Analyze JSON files from existing file paths through complete pipeline:
    JSON → Extract Data (Pydantic) → Convert to JSON → Pain Points (AI) → Market Gaps (AI) → JSON Response
    
    Args:
        request: JSONFilePathRequest containing JSON file paths and optional parameters
    
    Returns:
        JSON response with market gap solutions and pain points analysis
    """
    temp_dir = None
    
    try:
        # Validate that all files exist and are JSON
        for file_path in request.file_paths:
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found: {file_path}"
                )
            if not file_path.endswith('.json'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file_path} is not a JSON file. Only .json files are accepted."
                )
        
        # Create temporary directory for intermediate files
        temp_dir = tempfile.mkdtemp()
        
        # Step 1: Extract data from JSON files
        processed_data = json_extraction.process_multiple_json_files(request.file_paths)
        
        # Step 2: Save extracted data as JSON
        extracted_json_path = os.path.join(temp_dir, "extracted_data.json")
        with open(extracted_json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data.model_dump(), f, indent=2, ensure_ascii=False)
        
        # Step 3: Extract pain points from JSON data directly
        pain_points_result = extract_pain_points(
            file_paths=[extracted_json_path],
            model=request.model,
            temperature=request.temperature,
            input_format="json"
        )
        
        if pain_points_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Pain point extraction failed: {pain_points_result.get('error', 'Unknown error')}"
            )
        
        # Step 4: Generate market gap solutions
        solutions_result = generate_solutions(
            pain_points_data=pain_points_result["data"],
            model=request.model,
            temperature=request.temperature + 0.1
        )
        
        if solutions_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Solution generation failed: {solutions_result.get('error', 'Unknown error')}"
            )
        
        # Return structured response
        return PipelineResponse(
            market_gap_solutions=solutions_result["data"],
            pain_points=pain_points_result["data"],
            total_posts=processed_data.total_posts,
            total_comments=processed_data.total_comments_all,
            files_processed=[os.path.basename(f) for f in request.file_paths],
            status="success",
            message=f"Successfully processed {len(request.file_paths)} JSON file(s)"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}"
        )
    
    finally:
        # Cleanup temporary files
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

