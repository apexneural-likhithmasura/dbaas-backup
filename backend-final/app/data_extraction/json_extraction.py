import json
import os
import glob
from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import logging

# Note: These imports are not needed for the extraction utilities we're using
# The full pipeline functionality is handled by the API routes instead
# from pain_point_extractor import extract_pain_points
# from market_gap_generator import generate_solutions

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

    @validator('body', pre=True)
    def validate_body(cls, v):
        if v is None:
            return ""
        return str(v)


class PostModel(BaseModel):
    """Model for a Reddit post."""
    title: str = Field(..., description="Post title")
    content: str = Field(default="", description="Post content/selftext")

    @validator('title', pre=True)
    def validate_title(cls, v):
        if v is None:
            return ""
        return str(v)

    @validator('content', pre=True)
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


def extract_from_api_response_format(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract data from API response format (from /reddit/scrape-posts endpoint).
    
    Format:
    {
      "status": "success",
      "data": {
        "posts": [
          {
            "url": "...",
            "full_data": {
              "post": {...},
              "comments": [...]
            }
          }
        ]
      }
    }
    
    Args:
        data: API response data
        
    Returns:
        List of extracted post and comment data
    """
    extracted_posts = []
    
    # Navigate to the posts array
    posts_data = data.get("data", {}).get("posts", [])
    
    for post_item in posts_data:
        full_data = post_item.get("full_data")
        
        if not full_data:
            logger.warning(f"Skipping post {post_item.get('url', 'unknown')} - no full_data")
            continue
        
        # Extract using simplified format (full_data has 'post' and 'comments')
        extracted = extract_from_simple_format(full_data)
        extracted_posts.append(extracted)
    
    return extracted_posts


def extract_post_and_comments(json_file_path: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extract post title, content, and all comment bodies from JSON file.
    Supports multiple formats:
    1. Simplified format: {"post": {...}, "comments": [...]}
    2. Reddit API format: [{...post...}, {...comments...}]
    3. API Response format: {"status": "success", "data": {"posts": [...]}}
    
    Args:
        json_file_path: Path to the JSON file
        
    Returns:
        Dictionary or List containing post data and all comments
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Determine format and extract accordingly
    if isinstance(data, dict):
        # Check if it's API response format (has status/data/posts)
        if "status" in data and "data" in data and isinstance(data.get("data"), dict):
            if "posts" in data["data"]:
                # API Response format from /reddit/scrape-posts
                logger.info("Detected API response format (from /reddit/scrape-posts endpoint)")
                return extract_from_api_response_format(data)
        
        # Check if it's simplified format
        if "post" in data:
            # Simplified format
            logger.info("Detected simplified format")
            return extract_from_simple_format(data)
    
    elif isinstance(data, list):
        # Reddit API format
        logger.info("Detected Reddit API format")
        return extract_from_reddit_api_format(data)
    
    raise ValueError(f"Unknown JSON format in file: {json_file_path}")


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
            
            # Handle different return types (dict for single post, list for multiple posts)
            posts_to_process = []
            if isinstance(extracted, list):
                # API response format returns list of posts
                posts_to_process = extracted
                logger.info(f"Found {len(extracted)} posts in API response format")
            else:
                # Single post format
                posts_to_process = [extracted]
            
            # Process each extracted post
            for post_data in posts_to_process:
                # Create validated model
                post_model = PostModel(
                    title=post_data['post']['title'],
                    content=post_data['post'].get('content', '')
                )
                
                comments_models = [
                    CommentModel(body=comment['body']) 
                    for comment in post_data['comments']
                ]
                
                extracted_data_model = ExtractedDataModel(
                    post=post_model,
                    comments=comments_models,
                    total_comments=post_data['total_comments'],
                    source_file=json_file
                )
                
                all_extracted_data.append(extracted_data_model)
                total_comments_count += post_data['total_comments']
                
                logger.info(f"✓ Extracted: {post_data['total_comments']} comments from post '{post_model.title[:60]}...'")
            
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
# NOTE: The run_complete_pipeline and main functions are not used in the API.
# The pipeline is handled through API endpoints instead.
# These functions are commented out to avoid import errors.
