from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


# ==================== Pydantic Models ====================

class SolutionConcept(BaseModel):
    """Model for a business solution concept"""
    name: str = Field(..., description="Clear descriptive name")
    explanation: str = Field(..., description="2-3 sentence explanation")
    key_features: List[str] = Field(..., description="Key features or components")
    value_proposition: str = Field(..., description="Primary value proposition")
    business_model: str = Field(..., description="Potential business model")
    pain_points_addressed: List[str] = Field(..., description="Pain points this addresses")


class FrameworkSolution(BaseModel):
    """Model for solutions from a specific framework"""
    framework_name: str = Field(..., description="Framework name (e.g., Market Segmentation)")
    solutions: List[SolutionConcept] = Field(..., description="Solution concepts from this framework")


class OpportunityAssessment(BaseModel):
    """Model for opportunity assessment"""
    rank: int = Field(..., description="Ranking position (1-3)")
    solution_name: str = Field(..., description="Solution name")
    market_size_potential: str = Field(..., description="Market size and growth potential")
    competitive_advantage: str = Field(..., description="Competitive advantage sustainability")
    implementation_feasibility: str = Field(..., description="Implementation feasibility")
    category_dominance_potential: str = Field(..., description="Potential for category dominance")


class MarketGapAnalysis(BaseModel):
    """Model for complete market gap analysis"""
    executive_summary: str = Field(..., description="Brief overview of market opportunity")
    framework_solutions: List[FrameworkSolution] = Field(..., description="Solutions by framework")
    opportunity_assessment: List[OpportunityAssessment] = Field(..., description="Top 3 opportunities ranked")


class MarketGapResponse(BaseModel):
    """Model for market gap generation response"""
    data: MarketGapAnalysis
    status: str = Field(..., description="Status: success or error")
    error: Optional[str] = Field(None, description="Error message if any")

# OpenRouter API configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

# Configure logging (terminal only)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# System prompt for solution generation with JSON output
SOLUTION_GENERATION_SYSTEM_PROMPT = """## Context

I've identified specific pain points within a market through research and customer feedback. Now I need to generate potential business solutions that address these pain points while creating unique value. Rather than rushing to an obvious solution, I want to systematically explore different approaches to solving these problems in ways that could stand out in the market. The goal is to discover opportunities others might miss by considering various dimensions of differentiation and value creation.

## Your Role

You are an expert Business Opportunity Strategist who specializes in identifying creative approaches to solving market problems. Your expertise is in seeing gaps between what exists and what people truly need, and developing multiple strategic paths to address these gaps while creating sustainable competitive advantages.

## Your Mission

1. Analyze the provided market pain points
2. Generate potential solutions using multiple strategic frameworks
3. Consider both capturing existing demand and creating new demand
4. Evaluate each solution for its potential to be "best in its category"
5. Identify unique angles and differentiators for each solution
6. Present a comprehensive yet practical set of business opportunities

## Solution Frameworks to Apply

### 1. Market Segmentation Framework

- Identify underserved sub-niches within the broader market
- Consider demographic, psychographic, or behavioral segments
- Explore solutions specifically optimized for these segments

### 2. Product Differentiation Framework

- Consider premium versions of existing solutions
- Explore streamlined/simplified versions focused on core needs
- Identify potential for specialized features or capabilities

### 3. Business Model Innovation Framework

- Explore subscription vs. one-time purchase models
- Consider freemium, marketplace, or platform approaches
- Identify potential for service-based extensions to products

### 4. Distribution & Marketing Framework

- Identify underutilized acquisition channels
- Consider community-based or content-driven approaches
- Explore partnership or integration opportunities

### 5. New Paradigm Framework

- Consider applications of emerging technologies
- Identify relevant new trends, regulations, or data sources
- Explore potential for creating entirely new categories

## Output Format

1. **Executive Summary**: Brief overview of the identified market opportunity and key solution themes
2. **For each framework, provide**:
    - 2-3 specific solution concepts
    - Key differentiators for each concept
    - Target audience specifics
    - Potential challenges to overcome
    - "Best in the world" potential assessment
3. **For each solution concept, include**:
    - Clear descriptive name
    - 2-3 sentence explanation
    - Key features or components
    - Primary value proposition
    - Potential business model
    - How it specifically addresses identified pain points
4. **Opportunity Assessment**: Conclude with a ranked evaluation of the top 3 solutions based on:
    - Market size and growth potential
    - Competitive advantage sustainability
    - Implementation feasibility
    - Potential for category dominance ("best in the world" potential)

## Examples

### Good Solution Generation:

**Market Gap: Difficulty finding comfortable work-from-home furniture for small spaces**

*Segmentation Approach Solution:* **Urban Apartment Workspace System**

- A modular, wall-mounted workstation designed specifically for apartments under 600 sq ft
- Features fold-away components, integrated cable management, and customizable configurations
- Target audience: Urban professionals in high-cost cities with minimal space
- Business model: Direct-to-consumer with professional installation option
- Differentiator: The only ergonomic system designed exclusively for micro-apartments, with every component optimized for minimal footprint

*Business Model Innovation Solution:* **Nomad Desk Subscription**

- Monthly subscription service providing high-quality, compact desks with free exchanges
- Allows users to upgrade, downsize, or change styles as their living situation changes
- Target audience: Young professionals who move frequently or want flexibility
- Business model: Recurring revenue with asset utilization optimization
- Differentiator: Eliminates the risk of investing in furniture that might not fit future spaces

## Output Instructions

- Begin by reviewing the pain points to understand the core market needs
- Apply each framework systematically to generate diverse solution approaches
- For each solution, clearly articulate how it addresses the specific pain points
- Evaluate each solution for its potential to be "best in its category" in some way
- Generate solutions across different price points and complexity levels
- Ensure solutions span both immediate tactical opportunities and longer-term strategic plays
- Prioritize practical, implementable ideas over theoretical concepts

## CRITICAL: JSON Output Format

You MUST return your analysis as a valid JSON object with the following EXACT structure:

```json
{
  "executive_summary": "Brief overview of the identified market opportunity and key solution themes",
  "framework_solutions": [
    {
      "framework_name": "Market Segmentation Framework",
      "solutions": [
        {
          "name": "Solution Name",
          "explanation": "2-3 sentence explanation",
          "key_features": ["Feature 1", "Feature 2", "Feature 3"],
          "value_proposition": "Primary value proposition",
          "business_model": "Potential business model description",
          "pain_points_addressed": ["Pain point 1", "Pain point 2"]
        }
      ]
    }
  ],
  "opportunity_assessment": [
    {
      "rank": 1,
      "solution_name": "Top Solution Name",
      "market_size_potential": "Assessment of market size and growth",
      "competitive_advantage": "Competitive advantage sustainability",
      "implementation_feasibility": "Implementation feasibility assessment",
      "category_dominance_potential": "Potential for category dominance"
    }
  ]
}
```

Return ONLY valid JSON format as specified above. Do not include any text before or after the JSON object."""


def generate_solutions(pain_points_data: Dict[str, Any],
                      api_key: str = None,
                      model: str = None,
                      temperature: float = 0.8,
                      output_file: str = None) -> Dict[str, Any]:
    """
    Generate business solutions based on identified pain points.
    
    Args:
        pain_points_data: Dictionary containing pain point analysis (from pain point extractor)
        api_key: OpenRouter API key (optional, uses OPENROUTER_API_KEY env var if not provided)
        model: Model to use (default: "anthropic/claude-3.5-sonnet")
        temperature: Model temperature (default: 0.8)
        output_file: Path to save the solution output (optional)
    
    Returns:
        Dictionary with:
            - data: Text response with solution recommendations
            - status: "success" or "error"
            - error: Error message if status is "error"
            - output_file: Path to saved file if output_file was provided
    
    Example:
        >>> # Load pain points from the pain point extractor output
        >>> with open("pain_points_analysis.json", "r") as f:
        ...     pain_points = json.load(f)
        >>> 
        >>> # Generate solutions
        >>> result = generate_solutions(
        ...     pain_points_data=pain_points,
        ...     output_file="business_solutions.txt"
        ... )
        >>> 
        >>> if result["status"] == "success":
        ...     print(result["data"])
    """
    if model is None:
        model = OPENROUTER_DEFAULT_MODEL
    
    start_time = datetime.now()
    logger.info("="*80)
    logger.info("Starting business solution generation")
    logger.info(f"Timestamp: {start_time}")
    logger.info(f"Model: {model}")
    logger.info(f"Temperature: {temperature}")
    
    try:
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            logger.info("Using OpenRouter API key from environment variables")
        else:
            logger.info("Using OpenRouter API key from function parameter")
        
        if not api_key:
            error_msg = "OPENROUTER_API_KEY not found in environment variables or parameters"
            logger.error(error_msg)
            return {
                "data": "",
                "status": "error",
                "error": error_msg
            }
        
        pain_points_text = json.dumps(pain_points_data, indent=2, ensure_ascii=False)
        logger.info(f"Pain points data length: {len(pain_points_text)} characters")
        
        logger.info("Initializing Claude via OpenRouter")
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL
        )
        
        messages = [
            SystemMessage(content=SOLUTION_GENERATION_SYSTEM_PROMPT),
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
            logger.error(f"Response text: {solutions_text[:500]}...")
            # Return text format as fallback
            return {
                "data": {"executive_summary": solutions_text, "framework_solutions": [], "opportunity_assessment": []},
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


def example_usage():
    """
    Example of how to use the generate_solutions function.
    """
    logger.info("Running example usage")
    
    # Example 1: Load pain points from JSON file (output from pain point extractor)
    pain_points_file = "/root/DBASS/fastapi2/pain_point_analysis.json"
    
    try:
        with open(pain_points_file, 'r', encoding='utf-8') as f:
            pain_points_data = json.load(f)
        
        # Generate solutions
        result = generate_solutions(
            pain_points_data=pain_points_data,
            output_file="./business_solutions.txt"
        )
        
        if result["status"] == "success":
            print("\n" + "=" * 80)
            print("Business Solution Generation Results:")
            print("=" * 80)
            print(result["data"])
            print("=" * 80)
            
            if "output_file" in result:
                print(f"\nSolutions saved to: {result['output_file']}")
        else:
            print(f"\nError: {result['error']}")
    
    except FileNotFoundError:
        print(f"\nError: Pain points file not found: {pain_points_file}")
        print("Please run the pain point extractor first to generate pain_point_analysis.json")
    
    # Example 2: Direct pain points data
    #
    print("\n" + "=" * 80)
    print("Example 2: Using sample pain points data")
    print("=" * 80)
    
    result = generate_solutions(
        pain_points_data=pain_points_data,
        output_file="./sample_solutions.txt"
    )
    
    if result["status"] == "success":
        print("\n✅ Solutions generated successfully!")
        print(f"Preview: {result['data'][:300]}...")
    else:
        print(f"\n❌ Error: {result['error']}")


if __name__ == "__main__":
    example_usage()