from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import tempfile
import shutil
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the extractor and generator functions
from pain_point_extractor import extract_pain_points
from market_gap_generator import generate_solutions

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Pain Point & Market Gap Analyzer API",
    description="API to extract pain points from Reddit data and generate business solutions",
    version="1.0.0"
)


class AnalysisResponse(BaseModel):
    """Response model for the complete analysis"""
    pain_points: dict
    market_solutions: str
    status: str
    message: Optional[str] = None


class FilePathRequest(BaseModel):
    """Request model for analyzing existing files"""
    file_paths: List[str]
    model: Optional[str] = "anthropic/claude-3.5-sonnet"
    temperature: Optional[float] = 0.7


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Pain Point & Market Gap Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze-files": "POST - Upload TXT files for analysis",
            "/analyze-paths": "POST - Analyze files from existing paths",
            "/health": "GET - Health check"
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


@app.post("/analyze-files", response_model=AnalysisResponse)
async def analyze_uploaded_files(
    files: List[UploadFile] = File(...),
    model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.7
):
    """
    Analyze uploaded TXT files to extract pain points and generate market solutions.
    
    Args:
        files: List of TXT files containing Reddit conversations
        model: AI model to use (default: anthropic/claude-3.5-sonnet)
        temperature: Model temperature (default: 0.7)
    
    Returns:
        JSON response containing pain points analysis and business solutions
    """
    temp_dir = None
    
    try:
        # Validate files
        for file in files:
            if not file.filename.endswith('.txt'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a TXT file. Only .txt files are accepted."
                )
        
        # Create temporary directory to store uploaded files
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        # Save uploaded files
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            file_paths.append(file_path)
        
        # Step 1: Extract pain points
        pain_points_result = extract_pain_points(
            file_paths=file_paths,
            model=model,
            temperature=temperature
        )
        
        if pain_points_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Pain point extraction failed: {pain_points_result.get('error', 'Unknown error')}"
            )
        
        # Step 2: Generate market solutions using the extracted pain points
        solutions_result = generate_solutions(
            pain_points_data=pain_points_result["data"],
            model=model,
            temperature=temperature + 0.1  # Slightly higher temperature for creative solutions
        )
        
        if solutions_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Solution generation failed: {solutions_result.get('error', 'Unknown error')}"
            )
        
        # Return combined results
        return AnalysisResponse(
            pain_points=pain_points_result["data"],
            market_solutions=solutions_result["data"],
            status="success",
            message=f"Successfully analyzed {len(files)} file(s)"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during analysis: {str(e)}"
        )
    
    finally:
        # Cleanup temporary files
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.post("/analyze-paths")
async def analyze_file_paths(request: FilePathRequest):
    """
    Analyze files from existing file paths to extract pain points and generate market solutions.
    
    Args:
        request: FilePathRequest containing file paths and optional parameters
    
    Returns:
        JSON response containing pain points analysis and business solutions
    """
    try:
        # Validate that all files exist
        for file_path in request.file_paths:
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found: {file_path}"
                )
            if not file_path.endswith('.txt'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file_path} is not a TXT file. Only .txt files are accepted."
                )
        
        # Step 1: Extract pain points
        pain_points_result = extract_pain_points(
            file_paths=request.file_paths,
            model=request.model,
            temperature=request.temperature
        )
        
        if pain_points_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Pain point extraction failed: {pain_points_result.get('error', 'Unknown error')}"
            )
        
        # Step 2: Generate market solutions using the extracted pain points
        solutions_result = generate_solutions(
            pain_points_data=pain_points_result["data"],
            model=request.model,
            temperature=request.temperature + 0.1  # Slightly higher temperature for creative solutions
        )
        
        if solutions_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Solution generation failed: {solutions_result.get('error', 'Unknown error')}"
            )
        
        # Return combined results
        return {
            "pain_points": pain_points_result["data"],
            "market_solutions": solutions_result["data"],
            "status": "success",
            "message": f"Successfully analyzed {len(request.file_paths)} file(s)"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during analysis: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

