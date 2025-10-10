import json
import os
import glob
from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import logging

# Import the pain point extractor and market gap generator
from pain_point_extractor import extract_pain_points
from market_gap_generator import generate_solutions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Pydantic Models ====================

class CommentModel(BaseModel):
    """Model for a single comment."""
    body: str = Field(..., description="Comment text content")

    @field_validator('body')
    @classmethod
    def validate_body(cls, v):
        if v is None:
            return ""
        return str(v)


class PostModel(BaseModel):
    """Model for a Reddit post."""
    title: str = Field(..., description="Post title")
    content: str = Field(default="", description="Post content/selftext")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is None:
            return ""
        return str(v)

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if v is None:
            return ""
        return str(v)


class ExtractedDataModel(BaseModel):
    """Model for extracted post and comments data."""
    post: PostModel
    comments: List[CommentModel]
    total_comments: int = Field(..., description="Total number of comments extracted")
    source_file: Optional[str] = Field(None, description="Source JSON file path")


class ProcessedDataModel(BaseModel):
    """Model for data from multiple files."""
    extracted_data: List[ExtractedDataModel]
    total_posts: int = Field(..., description="Total number of posts processed")
    total_comments_all: int = Field(..., description="Total comments across all posts")
    processed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class PipelineResultModel(BaseModel):
    """Model for the complete pipeline result."""
    extracted_data: ProcessedDataModel
    pain_points: Optional[Dict[str, Any]] = Field(None, description="Pain points analysis result")
    market_gaps: Optional[str] = Field(None, description="Market gap solutions")
    status: str = Field(..., description="Pipeline status: success or error")
    error: Optional[str] = Field(None, description="Error message if any")
    files_processed: List[str] = Field(default_factory=list)
    output_files: Dict[str, str] = Field(default_factory=dict)


# ==================== Extraction Functions ====================

def extract_nested_comments_simple(comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recursively extract comment bodies from simplified nested comment structure.
    
    Args:
        comments: List of comment dictionaries
        
    Returns:
        List of dictionaries containing comment body only
    """
    extracted_comments = []
    
    for comment in comments:
        # Extract comment body only
        comment_data = {
            "body": comment.get("body")
        }
        extracted_comments.append(comment_data)
        
        # Recursively extract replies if they exist
        if comment.get("replies") and len(comment["replies"]) > 0:
            nested = extract_nested_comments_simple(comment["replies"])
            extracted_comments.extend(nested)
    
    return extracted_comments


def extract_nested_comments_reddit_api(comment_data: Union[Dict, List]) -> List[Dict[str, Any]]:
    """
    Recursively extract comment bodies from Reddit API format.
    
    Args:
        comment_data: Comment data from Reddit API (can be dict with 'kind' and 'data', or a list)
        
    Returns:
        List of dictionaries containing comment body only
    """
    extracted_comments = []
    
    # Handle Listing kind (list of comments)
    if isinstance(comment_data, dict) and comment_data.get("kind") == "Listing":
        children = comment_data.get("data", {}).get("children", [])
        for child in children:
            extracted_comments.extend(extract_nested_comments_reddit_api(child))
        return extracted_comments
    
    # Handle individual comment (t1)
    if isinstance(comment_data, dict) and comment_data.get("kind") == "t1":
        data = comment_data.get("data", {})
        comment = {
            "body": data.get("body")
        }
        extracted_comments.append(comment)
        
        # Process replies
        replies = data.get("replies")
        if replies and isinstance(replies, dict):
            nested = extract_nested_comments_reddit_api(replies)
            extracted_comments.extend(nested)
    
    return extracted_comments


def extract_from_simple_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract data from simplified format (with 'post' and 'comments' keys)."""
    post = data.get("post", {})
    post_data = {
        "title": post.get("title"),
        "content": post.get("selftext", "")
    }
    
    comments = data.get("comments", [])
    all_comments = extract_nested_comments_simple(comments)
    
    return {
        "post": post_data,
        "comments": all_comments,
        "total_comments": len(all_comments)
    }


def extract_from_reddit_api_format(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract data from Reddit API format (list with post and comments)."""
    if not data or len(data) < 1:
        return {"post": {}, "comments": [], "total_comments": 0}
    
    # First item is the post
    post_listing = data[0]
    if post_listing.get("kind") == "Listing":
        children = post_listing.get("data", {}).get("children", [])
        if children and children[0].get("kind") == "t3":
            post_data_raw = children[0].get("data", {})
            post_data = {
                "title": post_data_raw.get("title"),
                "content": post_data_raw.get("selftext", "")
            }
        else:
            post_data = {}
    else:
        post_data = {}
    
    # Second item contains comments
    all_comments = []
    if len(data) > 1:
        comments_listing = data[1]
        all_comments = extract_nested_comments_reddit_api(comments_listing)
    
    return {
        "post": post_data,
        "comments": all_comments,
        "total_comments": len(all_comments)
    }


def extract_post_and_comments(json_file_path: str) -> Dict[str, Any]:
    """
    Extract post title, content, and all comment bodies from JSON file.
    Supports both simplified format and Reddit API format.
    
    Args:
        json_file_path: Path to the JSON file
        
    Returns:
        Dictionary containing post data and all comments
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Determine format and extract accordingly
    if isinstance(data, dict) and "post" in data:
        # Simplified format
        return extract_from_simple_format(data)
    elif isinstance(data, list):
        # Reddit API format
        return extract_from_reddit_api_format(data)
    else:
        raise ValueError("Unknown JSON format")


# ==================== Multi-file Processing ====================

def process_multiple_json_files(json_files: List[str]) -> ProcessedDataModel:
    """
    Process multiple JSON files and extract all post and comment data.
    
    Args:
        json_files: List of paths to JSON files
        
    Returns:
        ProcessedDataModel containing all extracted data
    """
    logger.info(f"Processing {len(json_files)} JSON files...")
    
    all_extracted_data = []
    total_comments_count = 0
    
    for i, json_file in enumerate(json_files, 1):
        logger.info(f"Processing file {i}/{len(json_files)}: {json_file}")
        
        try:
            # Extract data from file
            extracted = extract_post_and_comments(json_file)
            
            # Create validated model
            post_model = PostModel(
                title=extracted['post']['title'],
                content=extracted['post'].get('content', '')
            )
            
            comments_models = [
                CommentModel(body=comment['body']) 
                for comment in extracted['comments']
            ]
            
            extracted_data_model = ExtractedDataModel(
                post=post_model,
                comments=comments_models,
                total_comments=extracted['total_comments'],
                source_file=json_file
            )
            
            all_extracted_data.append(extracted_data_model)
            total_comments_count += extracted['total_comments']
            
            logger.info(f"✓ Extracted: {extracted['total_comments']} comments from {os.path.basename(json_file)}")
            
        except Exception as e:
            logger.error(f"✗ Error processing {json_file}: {str(e)}")
            raise
    
    processed_data = ProcessedDataModel(
        extracted_data=all_extracted_data,
        total_posts=len(all_extracted_data),
        total_comments_all=total_comments_count
    )
    
    logger.info(f"Successfully processed {len(all_extracted_data)} posts with {total_comments_count} total comments")
    
    return processed_data


def convert_to_text_format(processed_data: ProcessedDataModel) -> str:
    """
    Convert processed data to text format for pain point extractor.
    
    Args:
        processed_data: Processed data model
        
    Returns:
        Formatted text string
    """
    text_parts = []
    
    for i, data in enumerate(processed_data.extracted_data, 1):
        text_parts.append("=" * 80)
        text_parts.append(f"POST {i}: {data.post.title}")
        text_parts.append("=" * 80)
        text_parts.append(f"\n{data.post.content}\n")
        text_parts.append("\n--- COMMENTS ---\n")
        
        for j, comment in enumerate(data.comments, 1):
            text_parts.append(f"\nComment {j}:")
            text_parts.append(comment.body)
        
        text_parts.append("\n\n")
    
    return "\n".join(text_parts)


def save_text_file(text_content: str, output_path: str) -> str:
    """
    Save text content to a file.
    
    Args:
        text_content: Text to save
        output_path: Output file path
        
    Returns:
        Path to saved file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    logger.info(f"Text data saved to: {output_path}")
    return output_path


def find_json_files(directory: str, pattern: str = "*.json") -> List[str]:
    """
    Find all JSON files in a directory.
    
    Args:
        directory: Directory to search
        pattern: File pattern (default: "*.json")
        
    Returns:
        List of JSON file paths
    """
    search_pattern = os.path.join(directory, pattern)
    json_files = glob.glob(search_pattern)
    logger.info(f"Found {len(json_files)} JSON files in {directory}")
    return sorted(json_files)


# ==================== Pipeline Function ====================

def run_complete_pipeline(
    json_files: Union[List[str], str],
    output_dir: str = "./output",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> PipelineResultModel:
    """
    Run complete pipeline: JSON extraction -> Pain Point Analysis -> Market Gap Generation.
    
    Args:
        json_files: List of JSON file paths OR directory path containing JSON files
        output_dir: Directory to save output files
        api_key: OpenRouter API key (optional)
        model: LLM model to use (optional)
        
    Returns:
        PipelineResultModel with all results
    """
    logger.info("=" * 80)
    logger.info("STARTING COMPLETE PIPELINE")
    logger.info("=" * 80)
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Handle directory input
        if isinstance(json_files, str) and os.path.isdir(json_files):
            json_files = find_json_files(json_files)
        
        if not json_files:
            raise ValueError("No JSON files provided")
        
        # Step 1: Extract data from JSON files
        logger.info("\n[STEP 1] Extracting data from JSON files...")
        processed_data = process_multiple_json_files(json_files)
        
        # Save extracted data
        extracted_json_path = os.path.join(output_dir, "extracted_data.json")
        with open(extracted_json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"Extracted data saved to: {extracted_json_path}")
        
        # Convert to text format for pain point extractor
        text_content = convert_to_text_format(processed_data)
        text_file_path = os.path.join(output_dir, "extracted_text.txt")
        save_text_file(text_content, text_file_path)
        
        # Step 2: Extract pain points
        logger.info("\n[STEP 2] Analyzing pain points...")
        pain_points_result = extract_pain_points(
            file_paths=[text_file_path],
            api_key=api_key,
            model=model
        )
        
        pain_points_data = None
        pain_points_json_path = os.path.join(output_dir, "pain_points.json")
        
        if pain_points_result["status"] == "success":
            pain_points_data = pain_points_result["data"]
            with open(pain_points_json_path, 'w', encoding='utf-8') as f:
                json.dump(pain_points_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Pain points saved to: {pain_points_json_path}")
        else:
            logger.error(f"Pain point extraction failed: {pain_points_result.get('error')}")
        
        # Step 3: Generate market gaps/solutions
        logger.info("\n[STEP 3] Generating market gap solutions...")
        market_gaps_text = None
        market_gaps_path = os.path.join(output_dir, "market_gaps.txt")
        
        if pain_points_data:
            market_gaps_result = generate_solutions(
                pain_points_data=pain_points_data,
                api_key=api_key,
                model=model,
                output_file=market_gaps_path
            )
            
            if market_gaps_result["status"] == "success":
                market_gaps_text = market_gaps_result["data"]
                logger.info(f"Market gaps saved to: {market_gaps_path}")
            else:
                logger.error(f"Market gap generation failed: {market_gaps_result.get('error')}")
        
        # Create final result
        result = PipelineResultModel(
            extracted_data=processed_data,
            pain_points=pain_points_data,
            market_gaps=market_gaps_text,
            status="success",
            files_processed=[os.path.basename(f) for f in json_files],
            output_files={
                "extracted_data": extracted_json_path,
                "extracted_text": text_file_path,
                "pain_points": pain_points_json_path,
                "market_gaps": market_gaps_path
            }
        )
        
        # Save final result
        final_output_path = os.path.join(output_dir, "pipeline_result.json")
        with open(final_output_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
        
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Final result saved to: {final_output_path}")
        
        return result
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        return PipelineResultModel(
            extracted_data=ProcessedDataModel(
                extracted_data=[],
                total_posts=0,
                total_comments_all=0
            ),
            status="error",
            error=str(e),
            files_processed=[]
        )


def main():
    """Main function to demonstrate extraction and pipeline."""
    import sys
    
    print("=" * 80)
    print("JSON EXTRACTION & PAIN POINT ANALYSIS PIPELINE")
    print("=" * 80)
    print()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Pipeline mode with command line arguments
        input_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./output"
        
        print(f"Running pipeline with:")
        print(f"  Input: {input_path}")
        print(f"  Output Directory: {output_dir}")
        print()
        
        # Run complete pipeline
        result = run_complete_pipeline(
            json_files=input_path,
            output_dir=output_dir
        )
        
        if result.status == "success":
            print("\n✅ Pipeline completed successfully!")
            print(f"\n📊 Summary:")
            print(f"  - Files processed: {len(result.files_processed)}")
            print(f"  - Total posts: {result.extracted_data.total_posts}")
            print(f"  - Total comments: {result.extracted_data.total_comments_all}")
            print(f"\n📁 Output files:")
            for key, path in result.output_files.items():
                print(f"  - {key}: {path}")
        else:
            print(f"\n❌ Pipeline failed: {result.error}")
    
    else:
        # Example usage mode
        print("EXAMPLE USAGE:\n")
        print("1. Single file extraction:")
        print("   python json-extraction.py /path/to/file.json")
        print()
        print("2. Multiple files from directory:")
        print("   python json-extraction.py /path/to/json/directory /path/to/output")
        print()
        print("3. Programmatic usage:")
        print()
        print("   # Process multiple JSON files")
        print("   from json_extraction import run_complete_pipeline")
        print()
        print("   result = run_complete_pipeline(")
        print("       json_files=['file1.json', 'file2.json'],  # or directory path")
        print("       output_dir='./output',")
        print("       api_key='your-api-key'  # optional")
        print("   )")
        print()
        print("   if result.status == 'success':")
        print("       print(result.pain_points)")
        print("       print(result.market_gaps)")
        print()
        print("=" * 80)
        print("\nRunning example with single file (if available)...")
        print()
        
        # Try example with default path
        example_file = "/root/DBASS/fastapi2/data.json"
        if os.path.exists(example_file):
            print(f"Processing example file: {example_file}")
            
            extracted_data = extract_post_and_comments(example_file)
            
            print("\n" + "=" * 80)
            print("POST INFORMATION")
            print("=" * 80)
            print(f"Title: {extracted_data['post']['title']}")
            content = extracted_data['post'].get('content', '')
            print(f"Content: {content[:200]}..." if len(content) > 200 else f"Content: {content}")
            
            print("\n" + "=" * 80)
            print(f"COMMENTS ({extracted_data['total_comments']} total)")
            print("=" * 80)
            
            for i, comment in enumerate(extracted_data['comments'][:10], 1):
                body_preview = comment['body'][:100] + "..." if len(comment['body']) > 100 else comment['body']
                print(f"\n{i}. {body_preview}")
            
            if extracted_data['total_comments'] > 10:
                print(f"\n... and {extracted_data['total_comments'] - 10} more comments")
            
            output_file = "./extracted_data_example.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Extracted data saved to: {output_file}")
        else:
            print(f"Example file not found: {example_file}")
            print("Please provide JSON file path as argument or update the example_file path")


if __name__ == "__main__":
    main()
