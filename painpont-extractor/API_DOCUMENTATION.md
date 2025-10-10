# API Documentation - Pain Point & Market Gap Analyzer

## Overview

This API accepts **multiple JSON files** containing Reddit posts/comments, extracts the data, analyzes pain points, and generates market gap solutions - all in a **single pipeline** with **structured JSON output**.

**Version:** 2.0.0  
**Base URL:** `http://localhost:8000`

## 🚀 What's New in v2.0

✅ **JSON File Support** - Upload or provide paths to JSON files  
✅ **Multi-File Processing** - Process multiple files at once  
✅ **Complete Pipeline** - JSON → Pain Points → Market Gaps  
✅ **Structured JSON Output** - Pydantic-validated responses  
✅ **No Extra Files** - Results returned directly in response  

## 📋 Endpoints

### 1. Health Check

**GET** `/health`

Check API status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "api_key_configured": true
}
```

### 2. Upload JSON Files for Analysis

**POST** `/analyze-json-files`

Upload multiple JSON files and get complete analysis.

**Parameters:**
- `files` (form-data): List of JSON files (required)
- `model` (query): AI model to use (default: "anthropic/claude-3.5-sonnet")
- `temperature` (query): Model temperature (default: 0.7)

**Request Example (cURL):**
```bash
curl -X POST "http://localhost:8000/analyze-json-files" \
  -F "files=@post1.json" \
  -F "files=@post2.json" \
  -F "files=@post3.json" \
  -F "model=anthropic/claude-3.5-sonnet" \
  -F "temperature=0.7"
```

**Request Example (Python):**
```python
import requests

files = [
    ('files', open('post1.json', 'rb')),
    ('files', open('post2.json', 'rb')),
    ('files', open('post3.json', 'rb'))
]

params = {
    'model': 'anthropic/claude-3.5-sonnet',
    'temperature': 0.7
}

response = requests.post(
    'http://localhost:8000/analyze-json-files',
    files=files,
    params=params
)

result = response.json()
print(result['market_gap_solutions'])
```

**Response Model:**
```json
{
  "market_gap_solutions": {
    "executive_summary": "Brief overview...",
    "framework_solutions": [
      {
        "framework_name": "Market Segmentation Framework",
        "solutions": [
          {
            "name": "Solution Name",
            "explanation": "Description...",
            "key_features": ["Feature 1", "Feature 2"],
            "value_proposition": "Value prop...",
            "business_model": "Business model...",
            "pain_points_addressed": ["Pain 1", "Pain 2"]
          }
        ]
      }
    ],
    "opportunity_assessment": [
      {
        "rank": 1,
        "solution_name": "Top Solution",
        "market_size_potential": "Large and growing...",
        "competitive_advantage": "Strong moat...",
        "implementation_feasibility": "Highly feasible...",
        "category_dominance_potential": "High potential..."
      }
    ]
  },
  "pain_points": {
    "summary": "Overview of pain points...",
    "categories": [
      {
        "category_name": "Category Name",
        "pain_points": [
          {
            "heading": "Pain Point Heading",
            "summary": "Summary...",
            "quotes": ["Quote 1", "Quote 2"],
            "frequency_intensity": "High frequency..."
          }
        ]
      }
    ],
    "priority_ranking": [
      {
        "rank": 1,
        "pain_point": "Description...",
        "frequency": "high",
        "intensity": "high",
        "specificity": "high",
        "solvability": "high",
        "reasoning": "Explanation..."
      }
    ]
  },
  "total_posts": 3,
  "total_comments": 245,
  "files_processed": ["post1.json", "post2.json", "post3.json"],
  "status": "success",
  "message": "Successfully processed 3 JSON file(s)"
}
```

### 3. Analyze JSON Files from Paths

**POST** `/analyze-json-paths`

Provide file paths to existing JSON files on the server.

**Request Body:**
```json
{
  "file_paths": [
    "/path/to/post1.json",
    "/path/to/post2.json",
    "/path/to/post3.json"
  ],
  "model": "anthropic/claude-3.5-sonnet",
  "temperature": 0.7
}
```

**Request Example (Python):**
```python
import requests

data = {
    "file_paths": [
        "/data/reddit_post_1.json",
        "/data/reddit_post_2.json"
    ],
    "model": "anthropic/claude-3.5-sonnet",
    "temperature": 0.7
}

response = requests.post(
    'http://localhost:8000/analyze-json-paths',
    json=data
)

result = response.json()
```

**Response:** Same as `/analyze-json-files`

## 📊 Supported JSON Formats

### Format 1: Simple Format
```json
{
  "post": {
    "title": "Looking for productivity app recommendations",
    "selftext": "I've been struggling to find..."
  },
  "comments": [
    {
      "body": "I've tried 10 different apps...",
      "replies": [
        {
          "body": "Same here!"
        }
      ]
    }
  ]
}
```

### Format 2: Reddit API Format
```json
[
  {
    "kind": "Listing",
    "data": {
      "children": [
        {
          "kind": "t3",
          "data": {
            "title": "Post title",
            "selftext": "Post content"
          }
        }
      ]
    }
  },
  {
    "kind": "Listing",
    "data": {
      "children": [
        {
          "kind": "t1",
          "data": {
            "body": "Comment text",
            "replies": {...}
          }
        }
      ]
    }
  }
]
```

Both formats are automatically detected and processed!

## 🔧 Pydantic Models

### PipelineResponse
```python
class PipelineResponse(BaseModel):
    market_gap_solutions: Dict[str, Any]
    pain_points: Dict[str, Any]
    total_posts: int
    total_comments: int
    files_processed: List[str]
    status: str
    message: Optional[str]
```

### MarketGapAnalysis
```python
class MarketGapAnalysis(BaseModel):
    executive_summary: str
    framework_solutions: List[FrameworkSolution]
    opportunity_assessment: List[OpportunityAssessment]
```

### PainPointAnalysis
```python
class PainPointAnalysis(BaseModel):
    summary: str
    categories: List[PainPointCategory]
    priority_ranking: List[PriorityRanking]
```

## 🎯 Pipeline Flow

```
1. JSON Files (Upload/Paths)
         ↓
2. Extract Posts & Comments
         ↓
3. Convert to Text
         ↓
4. Analyze Pain Points (AI)
         ↓
5. Generate Market Gaps (AI)
         ↓
6. Return Structured JSON
```

## 💡 Usage Examples

### Example 1: Quick Analysis
```python
import requests

# Upload files
files = [
    ('files', open('reddit_data.json', 'rb'))
]

response = requests.post(
    'http://localhost:8000/analyze-json-files',
    files=files
)

data = response.json()

# Access market gap solutions
print("Executive Summary:")
print(data['market_gap_solutions']['executive_summary'])

print("\nTop Opportunities:")
for opp in data['market_gap_solutions']['opportunity_assessment']:
    print(f"{opp['rank']}. {opp['solution_name']}")
```

### Example 2: Batch Processing
```python
import requests
import glob

# Get all JSON files
json_files = glob.glob('./reddit_data/*.json')

# Upload all files
files = [('files', open(f, 'rb')) for f in json_files]

response = requests.post(
    'http://localhost:8000/analyze-json-files',
    files=files
)

result = response.json()
print(f"Processed {result['total_posts']} posts")
print(f"Analyzed {result['total_comments']} comments")
```

### Example 3: Access Structured Data
```python
result = response.json()

# Access pain points
for category in result['pain_points']['categories']:
    print(f"\nCategory: {category['category_name']}")
    for pain_point in category['pain_points']:
        print(f"  - {pain_point['heading']}")
        print(f"    Quotes: {len(pain_point['quotes'])}")

# Access market solutions
for framework in result['market_gap_solutions']['framework_solutions']:
    print(f"\n{framework['framework_name']}:")
    for solution in framework['solutions']:
        print(f"  - {solution['name']}")
        print(f"    Features: {', '.join(solution['key_features'])}")
```

## 🚨 Error Handling

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Errors

**400 Bad Request** - Invalid file format
```json
{
  "detail": "File data.txt is not a JSON file. Only .json files are accepted."
}
```

**404 Not Found** - File path doesn't exist
```json
{
  "detail": "File not found: /path/to/file.json"
}
```

**500 Internal Server Error** - Pipeline error
```json
{
  "detail": "Pain point extraction failed: API key not configured"
}
```

## 🔐 Authentication

Set your OpenRouter API key in `.env`:

```bash
OPENROUTER_API_KEY=your_api_key_here
```

## ⚙️ Configuration

### Available Models
- `anthropic/claude-3.5-sonnet` (default, recommended)
- `anthropic/claude-3-opus`
- `openai/gpt-4`
- Any OpenRouter supported model

### Temperature Range
- `0.0` - More deterministic
- `0.7` - Balanced (default)
- `1.0` - More creative

## 🧪 Testing the API

### Using cURL
```bash
# Health check
curl http://localhost:8000/health

# Upload files
curl -X POST "http://localhost:8000/analyze-json-files" \
  -F "files=@test.json"
```

### Using Python
```python
import requests

# Test health
response = requests.get('http://localhost:8000/health')
print(response.json())

# Test upload
files = [('files', open('test.json', 'rb'))]
response = requests.post(
    'http://localhost:8000/analyze-json-files',
    files=files
)
print(response.json())
```

### Using FastAPI Docs
Visit: `http://localhost:8000/docs` for interactive API documentation

## 📈 Performance

- **Multi-file support**: Process up to 100+ files in one request
- **Automatic validation**: Pydantic ensures data integrity
- **Error recovery**: Graceful handling with detailed errors
- **No file storage**: Results returned in response (no extra files created)

## 🔄 Comparison: Old vs New

### Old Workflow (v1.0)
```
1. Upload TXT files manually
2. Get text-based pain points
3. Get text-based solutions
4. Manual parsing required
```

### New Workflow (v2.0)
```
1. Upload JSON files
2. Get structured JSON with:
   - Pain points (validated)
   - Market gaps (validated)
   - Metadata (posts, comments count)
3. Ready to use!
```

## 📝 Best Practices

1. **Use multiple files**: Better insights from diverse data
2. **Check file format**: Ensure JSON matches supported formats
3. **Handle errors**: Implement proper error handling
4. **Parse response**: Use Pydantic models for type safety
5. **Monitor usage**: Track API calls and costs

## 🆘 Troubleshooting

**Issue**: "API key not configured"  
**Solution**: Set `OPENROUTER_API_KEY` in `.env` file

**Issue**: "Unknown JSON format"  
**Solution**: Ensure JSON matches one of the supported formats

**Issue**: "Pipeline error"  
**Solution**: Check logs, verify JSON structure, ensure API key is valid

## 📚 Additional Resources

- [Complete Pipeline Documentation](PIPELINE_README.md)
- [Quick Start Guide](QUICK_START.md)
- [Installation Guide](INSTALLATION.md)
- [Feature Summary](SUMMARY.md)

---

**Need Help?** Check the [troubleshooting section](INSTALLATION.md#troubleshooting) or review the example code.

