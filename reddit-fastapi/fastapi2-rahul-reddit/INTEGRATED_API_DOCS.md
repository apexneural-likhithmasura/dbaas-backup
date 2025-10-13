# 🚀 Integrated Reddit Pipeline API

## Overview

Complete end-to-end pipeline that takes a market query and returns pain points + market gap solutions!

```
User Query → Reddit Search → JSON Extraction → Pain Points → Market Gaps → Complete Analysis
```

## 🎯 What It Does

1. **User provides market query** (e.g., "productivity apps for remote workers")
2. **Searches Reddit** for relevant discussions
3. **Ranks posts** with AI
4. **Extracts JSON data** from top posts
5. **Analyzes pain points** with AI
6. **Generates market gap solutions** with AI
7. **Returns complete analysis** with opportunities

## 📋 New Endpoints

### 1. Start Complete Pipeline

**POST** `/pipeline/complete`

Start the complete pipeline with a market query.

**Request:**
```json
{
  "market": "productivity apps for remote workers",
  "num_results": 30,
  "top_n": 10,
  "deep_top_k": 5,
  "ai_model": "anthropic/claude-3.5-sonnet",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "message": "Complete pipeline job created",
  "data": {
    "job_id": "uuid-here",
    "market": "productivity apps for remote workers",
    "websocket_url": "/ws/jobs/{job_id}",
    "status_url": "/jobs/{job_id}/status",
    "result_url": "/jobs/{job_id}/result"
  },
  "status": "success"
}
```

### 2. Check Pipeline Status

**GET** `/pipeline/status`

Check if the pain point pipeline is available and configured.

**Response:**
```json
{
  "message": "Pipeline status",
  "data": {
    "pain_point_extractor_available": true,
    "openrouter_key_configured": true,
    "openai_key_configured": true
  },
  "status": "success"
}
```

### 3. Get Job Result

**GET** `/jobs/{job_id}/result`

Get the complete pipeline result.

**Response:**
```json
{
  "message": "Result fetched",
  "data": {
    "market": "productivity apps",
    "timestamp": "2025-10-10T12:00:00",
    "reddit_analysis": {
      "total_posts_found": 30,
      "posts_ranked": 10,
      "posts_deep_analyzed": 5
    },
    "pain_point_analysis": {
      "total_pain_points": 25,
      "categories": 5,
      "summary": "Users struggle with..."
    },
    "market_gaps": {
      "executive_summary": "Key opportunities...",
      "total_solutions": 15,
      "frameworks": 5,
      "top_opportunities": [...]
    },
    "pain_points": {...},
    "market_gap_solutions": {...},
    "extracted_data": {...},
    "output_dir": "..."
  },
  "status": "success"
}
```

### 4. Track Progress (WebSocket)

**WebSocket** `/ws/jobs/{job_id}`

Real-time progress updates.

**Messages:**
```json
// Log message
{"type": "log", "message": "STEP 1: Searching Reddit..."}

// Error
{"type": "error", "message": "Error details"}

// Result
{"type": "result", "data": {...}}

// Done
{"type": "done"}
```

## 🔄 Complete Pipeline Flow

```
1. User Query: "productivity apps for remote workers"
         ↓
2. Reddit Search → Find 30+ discussions
         ↓
3. AI Ranking → Rank top 10 posts
         ↓
4. JSON Extraction → Extract from top 5 posts
         ↓
5. Data Processing → Combine JSON files
         ↓
6. Pain Point Analysis → Identify 25+ pain points
         ↓
7. Market Gap Generation → Generate 15+ solutions
         ↓
8. Final Result → Complete analysis with opportunities
```

## 💻 Usage Examples

### Python Example

```python
import requests
import json

# 1. Start complete pipeline
response = requests.post(
    'http://localhost:8000/pipeline/complete',
    json={
        "market": "productivity apps for remote workers",
        "num_results": 30,
        "top_n": 10,
        "deep_top_k": 5
    }
)

job_data = response.json()['data']
job_id = job_data['job_id']
print(f"Job started: {job_id}")

# 2. Wait for completion (polling)
import time
while True:
    status_response = requests.get(
        f'http://localhost:8000/jobs/{job_id}/status'
    )
    status = status_response.json()['data']['status']
    print(f"Status: {status}")
    
    if status == "completed":
        break
    elif status == "failed":
        print("Job failed!")
        break
    
    time.sleep(5)

# 3. Get result
result_response = requests.get(
    f'http://localhost:8000/jobs/{job_id}/result'
)

result = result_response.json()['data']

# 4. Access analysis
print("\n=== PAIN POINTS ===")
print(result['pain_point_analysis']['summary'])

print("\n=== MARKET GAPS ===")
print(result['market_gaps']['executive_summary'])

print("\n=== TOP OPPORTUNITIES ===")
for opp in result['market_gaps']['top_opportunities']:
    print(f"{opp['rank']}. {opp['solution_name']}")
```

### WebSocket Example (Real-time)

```python
import asyncio
import websockets
import json

async def track_pipeline(job_id):
    uri = f"ws://localhost:8000/ws/jobs/{job_id}"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'log':
                print(data['message'])
            elif data['type'] == 'error':
                print(f"ERROR: {data['message']}")
            elif data['type'] == 'result':
                print("RESULT:", data['data'])
            elif data['type'] == 'done':
                print("Pipeline complete!")
                break

# Start pipeline first, then:
asyncio.run(track_pipeline('your-job-id'))
```

### cURL Example

```bash
# 1. Check status
curl http://localhost:8000/pipeline/status

# 2. Start pipeline
curl -X POST http://localhost:8000/pipeline/complete \
  -H "Content-Type: application/json" \
  -d '{
    "market": "productivity apps",
    "num_results": 30,
    "top_n": 10,
    "deep_top_k": 5
  }'

# 3. Check job status
curl http://localhost:8000/jobs/{job_id}/status

# 4. Get result
curl http://localhost:8000/jobs/{job_id}/result
```

## 📊 Output Structure

### pain_points
```json
{
  "summary": "Overview of identified pain points",
  "categories": [
    {
      "category_name": "Category Name",
      "pain_points": [
        {
          "heading": "Pain point heading",
          "summary": "Summary",
          "quotes": ["Quote 1", "Quote 2"],
          "frequency_intensity": "High"
        }
      ]
    }
  ],
  "priority_ranking": [...]
}
```

### market_gap_solutions
```json
{
  "executive_summary": "Overview of opportunities",
  "framework_solutions": [
    {
      "framework_name": "Market Segmentation",
      "solutions": [
        {
          "name": "Solution Name",
          "explanation": "Description",
          "key_features": ["Feature 1", "Feature 2"],
          "value_proposition": "Value prop",
          "business_model": "Business model",
          "pain_points_addressed": ["Pain 1"]
        }
      ]
    }
  ],
  "opportunity_assessment": [
    {
      "rank": 1,
      "solution_name": "Top Solution",
      "market_size_potential": "Large",
      "competitive_advantage": "Strong",
      "implementation_feasibility": "High",
      "category_dominance_potential": "High"
    }
  ]
}
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_key  # For pain point & market gap analysis
OPENAI_API_KEY=your_openai_key          # For post ranking

# Optional
BASE_OUTPUT_DIR=./output                # Output directory (default: d:/redditdemo/output)
```

### Pipeline Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `market` | - | Market/niche to explore (required) |
| `num_results` | 30 | Number of Reddit posts to search |
| `top_n` | 10 | Number of posts to rank |
| `deep_top_k` | 5 | Number of posts to analyze deeply |
| `ai_model` | anthropic/claude-3.5-sonnet | AI model for analysis |
| `temperature` | 0.7 | AI temperature |

## 🔧 Setup

### 1. Install Dependencies

```bash
cd /root/dbas/backend-final/reddit-fastapi/fastapi2-rahul-reddit

# Install reddit-fastapi requirements
pip install -r requirements.txt

# Install pain point extractor requirements
cd ../../painpont-extractor
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key
EOF
```

### 3. Run Server

```bash
cd /root/dbas/backend-final/reddit-fastapi/fastapi2-rahul-reddit
python api_app.py
```

Or with uvicorn:
```bash
uvicorn api_app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access API

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## 📁 Output Files

For each pipeline run, creates a folder with:

```
{market}_{timestamp}/
├── {market}_raw_posts.json                    # All scraped posts
├── {market}_ranked_posts.json                 # Ranked posts
├── {market}_post_rank_1.json                  # Individual post JSON
├── {market}_post_rank_2.json
├── {market}_extracted_data.json               # Combined extracted data
├── {market}_pain_points.json                  # Pain point analysis
├── {market}_market_gaps.json                  # Market gap solutions
└── {market}_complete_pipeline_result.json     # Final result
```

## 🚨 Error Handling

### Common Errors

**503: Pain point extractor not available**
- Check that pain point extractor is properly installed
- Verify file paths are correct

**400: OPENROUTER_API_KEY not configured**
- Add OPENROUTER_API_KEY to .env file

**404: No Reddit URLs found**
- Try different search query
- Increase num_results

**500: Pain point extraction failed**
- Check API key validity
- Check logs for details

## 📊 Performance

- **Reddit Search**: ~5-10 seconds
- **Post Ranking**: ~10-20 seconds (AI)
- **JSON Extraction**: ~2-5 seconds per post
- **Pain Point Analysis**: ~30-60 seconds (AI)
- **Market Gap Generation**: ~30-60 seconds (AI)

**Total**: ~2-4 minutes for complete pipeline

## 🎯 Use Cases

### 1. Market Research
```python
# Find opportunities in a market
result = run_pipeline("SaaS tools for developers")
```

### 2. Product Validation
```python
# Validate product idea
result = run_pipeline("scheduling apps for teams")
```

### 3. Competitive Analysis
```python
# Analyze competitor discussions
result = run_pipeline("CRM software for small business")
```

### 4. Pain Point Discovery
```python
# Discover user pain points
result = run_pipeline("fitness tracking apps")
```

## 🔗 API Integration Flow

```python
# Complete workflow
import requests

# 1. Check status
status = requests.get('http://localhost:8000/pipeline/status')
print(status.json())

# 2. Start pipeline
response = requests.post(
    'http://localhost:8000/pipeline/complete',
    json={"market": "your market here"}
)
job_id = response.json()['data']['job_id']

# 3. Track via WebSocket (real-time)
# or poll status endpoint

# 4. Get results
result = requests.get(
    f'http://localhost:8000/jobs/{job_id}/result'
)

# 5. Use the data
pain_points = result.json()['data']['pain_points']
market_gaps = result.json()['data']['market_gap_solutions']
```

## ✅ Success Response Example

```json
{
  "market": "productivity apps",
  "reddit_analysis": {
    "total_posts_found": 35,
    "posts_ranked": 10,
    "posts_deep_analyzed": 5
  },
  "pain_point_analysis": {
    "total_pain_points": 28,
    "categories": 6,
    "summary": "Users struggle with app complexity, poor sync..."
  },
  "market_gaps": {
    "executive_summary": "Key opportunity: Simple, reliable sync...",
    "total_solutions": 18,
    "frameworks": 5,
    "top_opportunities": [
      {
        "rank": 1,
        "solution_name": "Ultra-Simple Productivity Suite",
        "market_size_potential": "Large and growing...",
        ...
      }
    ]
  }
}
```

## 🎉 You're Ready!

The complete pipeline is now integrated and ready to use. Simply:

1. POST to `/pipeline/complete` with your market query
2. Track progress via WebSocket or polling
3. Get comprehensive analysis with pain points and solutions!

**Happy analyzing!** 🚀


