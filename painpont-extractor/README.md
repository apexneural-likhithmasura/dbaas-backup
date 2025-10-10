# Pain Point & Market Gap Analyzer API

Complete automated pipeline from topic to market gap solutions using AI-powered analysis and Reddit data.

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Required API Key
OPENROUTER_API_KEY=sk-or-...
```

Add this to your `.env` file in the `painpont-extractor` directory.

### 2. Install Dependencies

```bash
cd painpont-extractor
pip install -r requirements.txt
```

### 3. Start Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test API

```bash
curl -X POST "http://localhost:8000/pipeline/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "market": "senior yoga",
    "num_results": 20,
    "top_n": 8,
    "deep_top_k": 3
  }'
```

---

## 📊 Complete Pipeline Flow

```
Market Query
    ↓
Reddit Search & Scraping
    ↓
AI Ranking (Claude 3.5 Sonnet)
    ↓
Pain Point Extraction (Claude 3.5 Sonnet)
    ↓
Market Gap Solutions (Claude 3.5 Sonnet)
```

---

## 🎯 API Endpoints

### 1. **Complete Pipeline** (Recommended)

**Endpoint:** `POST /pipeline/complete`

**Description:** Complete automated pipeline from market query to market gap solutions.

**Request:**
```json
{
  "market": "senior yoga",
  "num_results": 30,
  "top_n": 10,
  "deep_top_k": 5
}
```

**Parameters:**
- `market` (required): The market/query to search Reddit for
- `num_results` (optional, default: 30): Number of Reddit posts to fetch
- `top_n` (optional, default: 10): Number of top posts to rank
- `deep_top_k` (optional, default: 5): Number of posts for deep analysis

**Response:**
```json
{
  "message": "✅ Complete pipeline finished successfully!",
  "status": "completed",
  "data": {
    "executive_summary": "...",
    "framework_solutions": [...],
    "opportunity_assessment": [...]
  }
}
```

**What it does:**
1. Searches Reddit for your market query
2. AI ranks posts by relevance
3. Deep analysis of top posts
4. Extracts pain points
5. Generates market gap solutions

---

### 2. **Generate Market Expansion**

**Endpoint:** `POST /generate-prompt`

**Description:** Generate market categories and niches from a topic (no Reddit search).

**Request:**
```json
{
  "topic": "fitness for seniors"
}
```

**Response:**
```json
{
  "message": "Prompt generated successfully",
  "status": "success",
  "data": {
    "topic": "fitness for seniors",
    "expanded_prompt": "{\"Health\": {\"Senior Fitness\": {...}}}",
    "timestamp": "2025-10-10T12:00:00"
  }
}
```

---


### 3. **Pipeline Status**

**Endpoint:** `GET /pipeline/status`

**Description:** Check if all components are available.

**Response:**
```json
{
  "available": true,
  "message": "Complete pipeline with Reddit scraping is available",
  "requirements": {
    "reddit_components": true,
    "openrouter_api_key": true
  },
  "ai_models": {
    "market_expansion": "anthropic/claude-3.5-sonnet (via OpenRouter)",
    "pain_point_extraction": "anthropic/claude-3.5-sonnet (via OpenRouter)",
    "market_gap_generation": "anthropic/claude-3.5-sonnet (via OpenRouter)"
  }
}
```

---


---

## 🔄 Pipeline Steps Explained

### Step 1: Market Expansion
- User provides broad topic (e.g., "fitness for seniors")
- Claude 3.5 Sonnet expands into market hierarchy
- Output: Categories, niches, sub-niches

**Example Output:**
```json
{
  "Health": {
    "Senior Fitness": {
      "Low-Impact Exercise": {
        "Chair Yoga": {},
        "Water Aerobics": {}
      }
    }
  }
}
```

### Step 2: Niche Extraction
- System parses market hierarchy
- Extracts specific, searchable niches
- Selects most relevant niche for Reddit search

**Example:**
- Extracted: ["Senior Fitness", "Chair Yoga", "Water Aerobics"]
- Selected: "Senior Fitness" (primary search term)

### Step 3: Reddit Search
- Searches Reddit using extracted niche
- More targeted than original topic
- Finds relevant discussions and pain points

### Step 4: AI Ranking
- Claude ranks posts by relevance
- Selects top N posts for deep analysis
- Ensures quality over quantity

### Step 5: Deep Analysis
- Scrapes full JSON for top posts
- Extracts all comments and replies
- Structured data extraction

### Step 6: Pain Point Extraction
- Claude analyzes Reddit data
- Identifies pain points and frustrations
- Categorizes and prioritizes

### Step 7: Market Gap Generation
- Claude generates business solutions
- Framework-based analysis
- Opportunity assessment and ranking

---

## 📁 Project Structure

```
painpont-extractor/
├── main.py                      # FastAPI application & endpoints
├── pain_point_extractor.py      # Pain point extraction logic
├── market_gap_generator.py      # Market gap solution generation
├── json-extraction.py           # JSON data processing
├── requirements.txt             # Python dependencies
├── .env                         # API keys (create this)
│
├── idea_expander/               # Market expansion module
│   ├── __init__.py
│   └── market_idea_expander.py  # Market expansion with Claude
│
├── reddit/                      # Reddit scraping components
│   ├── google_search.py         # Google search for Reddit URLs
│   ├── reddit_scraper.py        # Reddit post scraper
│   ├── openai_ranker.py         # AI-powered post ranking
│   └── view_post_content.py     # Post content viewer
│
└── output/                      # Generated results (auto-created)
    └── {topic}/
        ├── {topic}_post_rank_1.json
        ├── {topic}_extracted_data.json
        ├── {topic}_pain_points.json
        ├── {topic}_market_gaps.json
        └── {topic}_topic_to_market_gaps_result.json
```

---

## 💡 Use Cases

### 1. Market Research
**Input:** "remote work tools"
**Output:** Specific pain points in remote collaboration, validated business opportunities

### 2. Product Validation
**Input:** "meal prep for busy parents"
**Output:** Real user frustrations, market gaps, solution concepts

### 3. Niche Discovery
**Input:** "alternative medicine"
**Output:** Specific sub-niches, demand signals, opportunity assessment

### 4. Competitive Analysis
**Input:** "fitness tracking apps"
**Output:** User complaints about existing solutions, unmet needs

---

## 🔑 Environment Variables

Create a `.env` file:

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...

# Optional (for different AI models)
# All operations use Claude 3.5 Sonnet by default
```

Get your OpenRouter API key: [https://openrouter.ai/](https://openrouter.ai/)

---

## 📊 Response Structure

### Complete Pipeline Response

```json
{
  "message": "Success message",
  "status": "completed",
  "data": {
    "topic": "original user input",
    "market_query_used": "extracted niche used for search",
    "extracted_niches": ["list of all niches found"],
    
    "reddit_analysis": {
      "total_posts_found": 30,
      "posts_ranked": 10,
      "posts_deep_analyzed": 5
    },
    
    "pain_point_analysis": {
      "total_pain_points": 45,
      "categories": 6,
      "summary": "Overall pain point summary"
    },
    
    "market_gap_solutions": {
      "executive_summary": "High-level market analysis",
      
      "framework_solutions": [
        {
          "framework_name": "Market Segmentation Framework",
          "solutions": [
            {
              "name": "Solution Name",
              "explanation": "Why this solution works",
              "key_features": ["feature1", "feature2"],
              "value_proposition": "Core value",
              "business_model": "Revenue model",
              "pain_points_addressed": [1, 2, 3]
          }
        ]
      }
    ],
      
      "opportunity_assessment": [
      {
        "rank": 1,
          "solution_name": "Top Solution",
          "market_size_potential": "Market size estimate",
          "competitive_advantage": "What makes it unique",
          "implementation_feasibility": "How easy to build",
          "category_dominance_potential": "Market position potential"
        }
      ]
    },
    
    "output_dir": "/path/to/saved/files",
    "timestamp": "2025-10-10T12:00:00"
  }
}
```

---

## 🛠️ Advanced Usage

### Python Example

```python
import requests

# Complete pipeline
    response = requests.post(
    "http://localhost:8000/topic-to-market-gaps",
    json={
        "topic": "fitness for seniors",
        "num_results": 20,
        "top_n": 8,
        "deep_top_k": 3
    }
)

        result = response.json()
market_gaps = result['data']['market_gap_solutions']

# Print solutions
for solution in market_gaps['framework_solutions']:
    print(f"Framework: {solution['framework_name']}")
    for s in solution['solutions']:
        print(f"  - {s['name']}: {s['value_proposition']}")
```

### cURL Example

```bash
# Complete pipeline
curl -X POST "http://localhost:8000/topic-to-market-gaps" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "yoga for seniors",
    "num_results": 20,
    "top_n": 8,
    "deep_top_k": 3
  }' | jq .

# Just market expansion
curl -X POST "http://localhost:8000/generate-prompt" \
  -H "Content-Type: application/json" \
  -d '{"topic": "yoga for seniors"}' | jq .

# Check status
curl http://localhost:8000/pipeline/status | jq .
```

---

## 🔧 Configuration

### Customize Reddit Search

```json
{
  "topic": "your topic",
  "num_results": 50,    // More Reddit posts (default: 30)
  "top_n": 15,          // More posts to rank (default: 10)
  "deep_top_k": 8       // More deep analysis (default: 5)
}
```

### AI Model

All operations use Claude 3.5 Sonnet via OpenRouter:
- Market Expansion
- Pain Point Extraction
- Market Gap Generation

Model can be changed in the code if needed.

---

## 📝 Output Files

Each pipeline run saves:

```
output/{topic}/
├── {topic}_post_rank_1.json       # Top ranked Reddit post (full JSON)
├── {topic}_post_rank_2.json       # 2nd ranked post
├── {topic}_post_rank_N.json       # Nth ranked post
├── {topic}_extracted_data.json    # Processed Reddit data
├── {topic}_pain_points.json       # Pain point analysis
├── {topic}_market_gaps.json       # Market gap solutions
└── {topic}_topic_to_market_gaps_result.json  # Complete result
```

---

## 🚨 Troubleshooting

### "Reddit components not available"
```bash
pip install beautifulsoup4 lxml googlesearch-python openai
```

### "Invalid API key"
- Check `.env` file has `OPENROUTER_API_KEY`
- Get key from [openrouter.ai](https://openrouter.ai)

### "No Reddit posts found"
- Try a more popular/specific topic
- Increase `num_results` parameter
- Check your internet connection

### Server won't start
```bash
# Check port 8000 is available
lsof -i :8000

# Try different port
uvicorn main:app --reload --port 8001
```

---

## 📊 API Features

✅ **Complete Automation** - One endpoint, full pipeline
✅ **AI-Powered** - Claude 3.5 Sonnet for all analysis
✅ **Smart Niche Extraction** - Finds specific markets automatically
✅ **Real User Data** - Reddit discussions and pain points
✅ **Business Solutions** - Actionable market gap analysis
✅ **Structured Output** - JSON with Pydantic validation
✅ **File Saving** - All intermediate results saved
✅ **Error Handling** - Robust fallbacks and validation

---

## 🎯 Key Benefits

### 1. **Intelligent Market Discovery**
- AI expands your topic into specific niches
- Discovers markets you didn't know existed
- More targeted than manual research

### 2. **Real Validation**
- Uses actual Reddit discussions
- Real pain points from real users
- Market demand validation

### 3. **Actionable Solutions**
- Business model suggestions
- Value proposition frameworks
- Competitive advantage analysis
- Implementation feasibility

### 4. **Time Saving**
- Minutes instead of days
- Automated end-to-end
- No manual data collection

---

## 📞 API Information

**Base URL:** `http://localhost:8000`

**All Endpoints:**
- `POST /pipeline/complete` - Complete pipeline (Recommended)
- `POST /generate-prompt` - Market expansion only
- `GET /pipeline/status` - Check system status
- `GET /health` - Health check
- `GET /` - API information

**Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 🔄 Version

**Current Version:** 2.0.0

**AI Models:**
- Market Expansion: Claude 3.5 Sonnet (OpenRouter)
- Pain Point Extraction: Claude 3.5 Sonnet (OpenRouter)
- Market Gap Generation: Claude 3.5 Sonnet (OpenRouter)

**Key Features:**
- Topic to market gaps pipeline
- Intelligent niche extraction
- Reddit scraping and analysis
- Complete automation

---

## 📄 License

This project is part of the DBAS backend system.

---

## 🎉 Get Started

```bash
# 1. Set up environment
cd painpont-extractor
echo "OPENROUTER_API_KEY=your-key-here" > .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
uvicorn main:app --reload

# 4. Test it
curl -X POST "http://localhost:8000/topic-to-market-gaps" \
  -H "Content-Type: application/json" \
  -d '{"topic": "fitness for seniors"}'
```

**You're ready to discover market opportunities!** 🚀
