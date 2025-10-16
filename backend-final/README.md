# Pain Point & Market Gap Analyzer API

AI-powered pain point extraction and market gap analysis using Claude 3.5 Sonnet.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Usage Examples](#usage-examples)
- [Development](#development)

---

## 🎯 Overview

This API provides AI-powered tools for:
- **Pain Point Extraction**: Analyze text/Reddit data to identify pain points and frustrations
- **Market Gap Analysis**: Generate business solutions using 5 strategic frameworks
- **Market Idea Expansion**: Explore market opportunities across Health, Wealth, and Relationships
- **Reddit Research**: Search, scrape, and rank Reddit posts for market insights

**Version:** 3.0.0  
**AI Model:** Claude 3.5 Sonnet (via OpenRouter)

---

## ✨ Features

### 1. Pain Point Extraction
- Extract pain points from text or uploaded files
- Categorize by severity and impact
- Priority ranking with confidence scores
- Pattern recognition and trend analysis

### 2. Market Gap Generation
- 5 strategic frameworks: JTBD, Blue Ocean, Kano, Clayton's, Porter's Forces
- Solution concepts with viability scores
- Market opportunity assessment
- Implementation roadmaps

### 3. Market Idea Expansion
- Hierarchical market segmentation
- Health, Wealth, and Relationships categories
- Niche exploration and sub-niches
- Real-time streaming generation

### 4. Reddit Research
- Search Reddit for market-related discussions
- Scrape post metadata and comments
- AI-powered ranking by market potential
- Complete research pipeline

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### Installation

1. **Clone the repository**
   ```bash
   cd generative-ai-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   # Required
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   
   # Optional
   BASE_URL=http://localhost:8000/dbas
   ENVIRONMENT=development
   ```

4. **Run the application**
   ```bash
   python run.py
   ```
   
   Or alternatively:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

5. **Access the API**
   - **API Docs (Swagger):** http://localhost:8000/dbas/api/docs
   - **ReDoc:** http://localhost:8000/dbas/api/redoc
   - **Base API:** http://localhost:8000/dbas/api/

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | ✅ Yes | - | Your OpenRouter API key |
| `BASE_URL` | ❌ No | `http://localhost:8000/dbas` | Base URL for the API |
| `ENVIRONMENT` | ❌ No | `development` | Environment (development/production) |
| `OPENAI_API_KEY` | ❌ No | - | OpenAI API key (optional) |

### config.py Structure

```python
class Settings:
    # Application
    app_name: str = "Pain Point & Market Gap Analyzer API"
    app_version: str = "3.0.0"
    base_url: str = "http://localhost:8000/dbas"
    api_prefix: str = "/api"
    
    # API Keys
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # AI Configuration
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-3.5-sonnet"
    default_temperature: float = 0.7
```

---

## 🔗 API Endpoints

All endpoints follow this pattern:
```
{BASE_URL}{API_PREFIX}/{module}/{endpoint}
```

**Example:** `http://localhost:8000/dbas/api/pain-points/extract-text/`

### URL Breakdown
```
http://localhost:8000/dbas/api/pain-points/extract-text/
│                      │    │   │                        │
│                      │    │   │                        └─ Endpoint
│                      │    │   └────────────────────────── Module
│                      │    └────────────────────────────── API Prefix
│                      └─────────────────────────────────── App Name
└────────────────────────────────────────────────────────── Base Server
```

### Complete Endpoint List

#### Pain Points (`/api/pain-points`)

**1. Extract from Text**
```
POST /dbas/api/pain-points/extract-text/
```
Extract pain points from text data.

**2. Extract from Files**
```
POST /dbas/api/pain-points/extract-file/
```
Extract pain points from uploaded files.

---

#### Market Gaps (`/api/market-gaps`)

**3. Generate Solutions**
```
POST /dbas/api/market-gaps/generate/
```
Generate business solutions using strategic frameworks.

---

#### Market Ideas (`/api/market-ideas`)

**4. Generate Ideas**
```
POST /dbas/api/market-ideas/generate/
```
Generate market ideas for a specific topic.

**5. Stream Ideas**
```
GET /dbas/api/market-ideas/stream/
```
Stream market ideas in real-time.

---

#### Reddit Research (`/api/reddit`)

**6. Search Posts**
```
POST /dbas/api/reddit/search/
```
Search Reddit for market-related posts.

**7. Scrape Posts**
```
POST /dbas/api/reddit/scrape/
```
Scrape metadata from Reddit URLs.

**8. Rank Posts**
```
POST /dbas/api/reddit/rank/
```
Rank posts by market potential using AI.

**9. Complete Research**
```
POST /dbas/api/reddit/complete-research/
```
Execute full pipeline: search → scrape → rank.

---

## 📁 Project Structure

```
generative-ai-backend/
├── run.py                      # Application runner
├── requirements.txt            # Dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # This file
│
├── app/
│   ├── main.py                 # FastAPI application
│   │
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   └── logging.py          # Logging setup
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── route.py        # Main router
│   │       ├── pain_point_routes.py
│   │       ├── market_gap_routes.py
│   │       ├── market_idea_routes.py
│   │       └── reddit_routes.py
│   │
│   ├── agents/                 # AI agent implementations
│   │   ├── pain_point_extractor.py
│   │   ├── market_gap_generator.py
│   │   └── market_idea_expander.py
│   │
│   ├── reddit_researcher/      # Reddit research components
│   │   ├── searcher.py
│   │   ├── scraper.py
│   │   └── ranker.py
│   │
│   ├── models/                 # Pydantic models
│   │   ├── pain_point_models.py
│   │   ├── market_gap_models.py
│   │   ├── request_models.py
│   │   ├── response_models.py
│   │   └── reddit_models.py
│   │
│   └── prompts/                # System prompts
│       ├── pain_point_extractor_prompt.txt
│       ├── market_gap_generator_prompt.txt
│       └── market_idea_expander_prompt.txt
```

---

## 💡 Usage Examples

### Example 1: Extract Pain Points

```bash
curl -X POST "http://localhost:8000/dbas/api/pain-points/extract-text/" \
  -H "Content-Type: application/json" \
  -d '{
    "text_data": "I am frustrated with expensive gym memberships that I barely use. The equipment is always occupied and the trainers are not helpful."
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Pain points extracted successfully",
  "data": {
    "categories": [
      {
        "name": "Cost Issues",
        "pain_points": [
          {
            "description": "Expensive gym memberships",
            "severity": "High",
            "frequency": "Recurring"
          }
        ]
      }
    ]
  }
}
```

---

### Example 2: Complete Reddit Research

```bash
curl -X POST "http://localhost:8000/dbas/api/reddit/complete-research/" \
  -H "Content-Type: application/json" \
  -d '{
    "market": "fitness tracking apps",
    "num_results": 20,
    "top_n": 5
  }'
```

---

### Example 3: Generate Market Gaps

```bash
curl -X POST "http://localhost:8000/dbas/api/market-gaps/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "pain_points": {
      "categories": [...]
    },
    "target_audience": "fitness enthusiasts",
    "industry_context": "health and wellness"
  }'
```

---

## 🛠️ Development

### Running in Development Mode

```bash
# Set environment to development
export ENVIRONMENT=development

# Run with auto-reload
python run.py
```

### Route Structure

All routes use the clean `router.add_api_route()` pattern:

```python
# Example: pain_point_routes.py
from fastapi import APIRouter
from ...agents.pain_point_extractor import PainPointExtractorAgent
from ...core.config import settings

router = APIRouter()

async def extract_pain_points_text(request):
    """Handler function"""
    agent = PainPointExtractorAgent(
        api_key=settings.openrouter_api_key,
        model=settings.default_model
    )
    result = agent.extract(text_data=request.text_data)
    return {"success": True, "data": result}

# Register route
router.add_api_route('/extract-text/', extract_pain_points_text, methods=["POST"])
```

### Adding New Routes

1. Create route file in `app/api/routes/`
2. Define handler functions
3. Register routes using `router.add_api_route()`
4. Import in `app/api/routes/route.py`

---

## 🔧 Architecture

### Clean Modular Design

- **No Service Layer**: Routes call agents directly
- **Configuration-Based**: All settings from `config.py`
- **Agent Pattern**: Business logic in dedicated agents
- **Pydantic Models**: Strong typing and validation
- **Separate Prompts**: System prompts in dedicated files

### Request Flow

```
Client Request
    ↓
FastAPI Main App
    ↓
API Router (with prefix)
    ↓
Module Router (pain-points, reddit, etc.)
    ↓
Handler Function
    ↓
Agent Initialization (with config)
    ↓
Agent Method Execution
    ↓
Response
```

---

## 📊 Key Features

### ✅ Implemented
- ✅ Clean route structure with `router.add_api_route()`
- ✅ Modular architecture (agents, models, routes)
- ✅ Base URL configuration with app name
- ✅ Centralized API key management
- ✅ Comprehensive Pydantic models
- ✅ System prompts in separate files
- ✅ Reddit research pipeline
- ✅ Multiple AI agents
- ✅ CORS support
- ✅ Logging system

### 📝 Configuration Summary

| Component | Value |
|-----------|-------|
| Base URL | `http://localhost:8000/dbas` |
| API Prefix | `/api` |
| AI Model | Claude 3.5 Sonnet |
| Temperature | 0.7 |
| Total Routes | 9 |
| Total Agents | 3 + Reddit components |

---

## 🚀 Deployment

### Production Environment

1. **Set environment variables**
   ```bash
   BASE_URL=https://api.yourcompany.com/dbas
   ENVIRONMENT=production
   OPENROUTER_API_KEY=your_production_key
   ```

2. **Run with production settings**
   ```bash
   python run.py
   ```

3. **Access endpoints**
   ```
   https://api.yourcompany.com/dbas/api/pain-points/extract-text/
   ```

---

## 📄 License

This project is part of the Pain Point Extraction and Market Gap Analysis system.

---

## 🤝 Support

For issues or questions:
- Check the API documentation: `/dbas/api/docs`
- Review the configuration in `app/core/config.py`
- Ensure `OPENROUTER_API_KEY` is set correctly

---

## 🎉 Quick Reference

### Start Application
```bash
python run.py
```

### Access Documentation
```
http://localhost:8000/dbas/api/docs
```

### Test Endpoint
```bash
curl http://localhost:8000/dbas/api/pain-points/extract-text/
```

### Environment Setup
```bash
# .env file
OPENROUTER_API_KEY=your_key_here
BASE_URL=http://localhost:8000/dbas
```

---

**Built with ❤️ using FastAPI and Claude 3.5 Sonnet**
