from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import json
import logging
from typing import Dict, List, Tuple
from datetime import datetime

# Load environment variables
load_dotenv()

# OpenRouter API configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pain_point_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# System prompt for analysis
SYSTEM_PROMPT = """# **Context**

I'm analyzing Reddit conversations to identify common pain points and problems within a specific market. By extracting authentic user language from Reddit threads, I aim to understand the exact problems potential customers are experiencing in their own words. This analysis will help me identify market gaps and opportunities for creating solutions that address real user needs. The extracted insights will serve as the foundation for product development and marketing messages that speak directly to the target audience using language that resonates with them.

## **Your Role**

You are an expert Market Research Analyst specializing in analyzing conversational data to identify pain points, frustrations, and unmet needs expressed by real users. Your expertise is in distilling lengthy Reddit threads into clear, actionable insights while preserving the authentic language users employ to describe their problems.

## **Your Mission**

1. Carefully analyze provided Reddit conversations and comments
2. Identify distinct pain points, problems, and frustrations mentioned by users
3. Extract and organize these pain points into clear categories
4. For each pain point, include all direct quotes from users that best illustrate this specific problem
5. Extract EVERY valuable pain point - thoroughness is crucial

## **Analysis Criteria**

### **INCLUDE:**

- Specific problems users are experiencing (e.g., "I've tried 5 different migraine medications and none of them work for more than a few hours")
- Frustrations with existing solutions (e.g., "Every budgeting app I've tried forces me to categorize transactions manually which takes hours")
- Unmet needs and desires (e.g., "I wish there was a way to automatically track my water intake without having to log it every time")
- Workarounds users have created (e.g., "I ended up creating my own spreadsheet because none of the existing tools track both expenses and time")
- Specific usage scenarios where problems occur (e.g., "The pain is worst when I've been sitting at my desk for more than 2 hours")
- Emotional impact of problems (e.g., "The constant back pain has made it impossible to play with my kids, which is devastating")

### **DO NOT INCLUDE:**

- General discussion not related to problems or pain points
- Simple questions asking for advice without describing a problem
- Generic complaints without specific details
- Positive experiences or success stories (unless they contrast with a problem)
- Discussions about news, politics, or other topics unrelated to personal experiences

## **Output Format**

You MUST return your analysis as a valid JSON object with the following structure:

```json
{
  "summary": "Brief overview of major pain points identified",
  "categories": [
    {
      "category_name": "Category name (e.g., Problems with Existing Solutions)",
      "pain_points": [
        {
          "heading": "Clear descriptive heading",
          "summary": "1-2 sentence summary",
          "quotes": [
            "Direct user quote 1",
            "Direct user quote 2",
            "Direct user quote 3"
          ],
          "frequency_intensity": "Note on frequency/intensity"
        }
      ]
    }
  ],
  "priority_ranking": [
    {
      "rank": 1,
      "pain_point": "Pain point description",
      "frequency": "high/medium/low",
      "intensity": "high/medium/low",
      "specificity": "high/medium/low",
      "solvability": "high/medium/low",
      "reasoning": "Brief explanation of ranking"
    }
  ]
}
```

## **Examples**

Good Pain Point Extraction:

### Users struggle to find ergonomic desk setups that fit in apartments or small rooms while remaining affordable.

- "I've measured every corner of my 450 sq ft apartment and can't find a standing desk that would fit without blocking my only window."
- "Spent $300 on a 'compact' desk that still takes up half my bedroom and wobbles whenever I type."
- "Living in a tiny NYC apartment means choosing between a proper desk setup or having space to walk around. Currently using my kitchen counter which is killing my back."
- "Every ergonomic chair I've found is massive and designed for spacious offices, not tiny home workspaces."

Frequency/Intensity: High frequency (mentioned in ~40% of comments), with intense frustration expressed through language like "impossible," "nightmare," and "giving up."

## **Output Instructions**

- First, scan the entire Reddit data to identify recurring themes and pain points
- Create relevant category headers based on these pain points
- Extract ONLY specific problems, frustrations, and unmet needs
- For each pain point, include the most illustrative direct quotes from users
- Extract EVERY SINGLE valuable pain point that matches the criteria
- Preserve the EXACT original language - no modifications to user text
- Rank the pain points based on apparent importance to users
- If a potential solution is frequently mentioned or requested, note this in your analysis
- CRITICAL: Return ONLY valid JSON format as specified above. Do not include any text before or after the JSON object.

## **Paste your Reddit data below:**"""


def load_txt_file(file_path: str) -> str:
    """
    Load text data from a TXT file.
    
    Args:
        file_path: Path to the TXT file
    
    Returns:
        String content of the file
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a .txt file
    """
    logger.info(f"Loading text file: {file_path}")
    
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    if not file_path.lower().endswith('.txt'):
        error_msg = f"File must be a .txt file: {file_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        logger.info(f"Successfully loaded text file: {file_path}")
        logger.info(f"Text length: {len(data)} characters")
        return data
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(error_msg)
        raise


def load_multiple_txt_files(file_paths: List[str]) -> str:
    """
    Load and combine multiple TXT files.
    
    Args:
        file_paths: List of paths to TXT files
    
    Returns:
        Combined text from all files
    """
    logger.info(f"Loading {len(file_paths)} text files")
    combined_parts = []
    
    for i, file_path in enumerate(file_paths, 1):
        logger.info(f"Loading file {i}/{len(file_paths)}: {file_path}")
        
        try:
            data = load_txt_file(file_path)
            
            # Add separator between files
            combined_parts.append(f"\n{'='*80}")
            combined_parts.append(f"FILE {i}: {os.path.basename(file_path)}")
            combined_parts.append(f"{'='*80}\n")
            combined_parts.append(data)
            combined_parts.append("\n")
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            raise
    
    combined_text = "\n".join(combined_parts)
    logger.info(f"Successfully combined {len(file_paths)} files")
    logger.info(f"Total combined length: {len(combined_text)} characters")
    
    return combined_text


def extract_pain_points(file_paths: List[str], 
                        api_key: str = None,
                        model: str = None,
                        temperature: float = 0.7) -> Dict[str, any]:
    """
    Extract pain points from TXT files containing Reddit data using Claude via OpenRouter.
    
    Args:
        file_paths: List of paths to TXT files containing Reddit conversations
        api_key: OpenRouter API key (uses OPENROUTER_API_KEY env var if not provided)
        model: Model to use (default: "anthropic/claude-3.5-sonnet")
        temperature: Model temperature (default: 0.7)
    
    Returns:
        Dictionary with:
            - data: Structured JSON with pain point analysis
            - status: "success" or "error"
            - error: Error message if status is "error"
    
    Example:
        >>> result = extract_pain_points(["data1.txt", "data2.txt"])
        >>> if result["status"] == "success":
        ...     print(json.dumps(result["data"], indent=2))
    """
    # Set default model
    if model is None:
        model = OPENROUTER_DEFAULT_MODEL
    
    # Validate input
    if not isinstance(file_paths, list):
        error_msg = "file_paths must be a list of file paths"
        logger.error(error_msg)
        return {"data": {}, "status": "error", "error": error_msg}
    
    if not file_paths:
        error_msg = "file_paths list cannot be empty"
        logger.error(error_msg)
        return {"data": {}, "status": "error", "error": error_msg}
    
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("Starting pain point extraction")
    logger.info(f"Timestamp: {start_time}")
    logger.info(f"Number of files: {len(file_paths)}")
    logger.info(f"Model: {model}")
    
    try:
        # Get API key
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                error_msg = "OPENROUTER_API_KEY not found in environment"
                logger.error(error_msg)
                return {"data": {}, "status": "error", "error": error_msg}
        
        # Load all TXT files
        logger.info("Loading TXT files...")
        reddit_text = load_multiple_txt_files(file_paths)
        
        # Initialize LLM
        logger.info(f"Initializing Claude via OpenRouter: {model}")
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://github.com/reddit-pain-point-analyzer",
                "X-Title": "Reddit Pain Point Analyzer"
            }
        )
        
        # Create messages
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
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
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed in {execution_time:.2f} seconds")
        logger.info("=" * 80)
        
        return {
            "data": analysis_json,
            "status": "success"
        }
    
    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        return {"data": {}, "status": "error", "error": str(e)}
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {"data": {}, "status": "error", "error": str(e)}
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return {"data": {}, "status": "error", "error": f"Failed to parse JSON: {str(e)}"}
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"data": {}, "status": "error", "error": str(e)}


def main():
    """
    Example usage of the pain point analyzer.
    """
    print("Reddit Pain Point Analyzer")
    print("=" * 80)
    
    # Example with multiple TXT files
    file_paths = [
        "test_data.txt",
        "test_data2.txt",
        "test_data3.txt"
    ]
    
    print(f"\nAnalyzing {len(file_paths)} text files...")
    print(f"Files: {', '.join(file_paths)}\n")
    
    result = extract_pain_points(file_paths)
    
    if result["status"] == "success":
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
        
        # Save to file
        output_file = "pain_point_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result["data"], f, indent=2, ensure_ascii=False)
        print(f"\n✓ Analysis saved to: {output_file}")
        
    else:
        print(f"\n✗ Error: {result['error']}")


if __name__ == "__main__":
    main()