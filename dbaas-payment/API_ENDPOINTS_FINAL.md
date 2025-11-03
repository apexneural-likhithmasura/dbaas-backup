# 🎯 Final API Endpoints - Clean & Essential

## ✅ 5 Essential Endpoints (Cleaned Up)

### 1. **Pain Point Extractor + Market Gap Generator** (Combined - File Input)

```bash
POST /dbas/api/pain-points/complete-analysis-file/
Content-Type: multipart/form-data

# Upload JSON or TXT file
files=@data.json
```

**Response:**
```json
{
  "success": true,
  "message": "Complete analysis pipeline executed successfully for 1 files",
  "data": {
    "pain_points": {
      "data": {
        "summary": "...",
        "categories": [...],
        "priority_ranking": [...]
      },
      "status": "success"
    },
    "market_gaps": {
      "data": {
        "solution_concepts": [...],
        "frameworks_applied": [...],
        "opportunity_assessment": [...]
      },
      "status": "success"
    }
  }
}
```

---

### 2. **Pain Point Extractor + Market Gap Generator** (Combined - Reddit/JSON Input)

```bash
POST /dbas/api/pain-points/complete-analysis-reddit/
Content-Type: application/json
```

**Accepts 3 input formats:**

#### Format 1: Direct (Recommended)
```json
{
  "post": {
    "title": "Post title",
    "selftext": "Post content",
    "author": "username",
    "score": 100
  },
  "comments": [
    {
      "author": "user1",
      "body": "Comment text",
      "score": 10,
      "depth": 0,
      "replies": []
    }
  ],
  "total_comments": 1
}
```

#### Format 2: From /reddit/scrape/ (Auto-unwraps)
```json
{
  "data": {
    "posts": [
      {
        "post": {...},
        "comments": [...]
      }
    ]
  }
}
```

#### Format 3: Array format
```json
{
  "posts": [
    {
      "post": {...},
      "comments": [...]
    }
  ]
}
```

**Response:** Same as complete-analysis-file (pain_points + market_gaps)

---

### 3. **Reddit Scraping** (Get Complete Post Data)

```bash
POST /dbas/api/reddit/scrape/
Content-Type: application/json

{
  "urls": [
    "https://www.reddit.com/r/yoga/comments/xyz..."
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Scraped complete data from 1 Reddit posts",
  "data": {
    "posts": [
      {
        "post": {
          "title": "...",
          "selftext": "Complete post content",
          "selftext_html": "HTML formatted content",
          "author": "username",
          "score": 129,
          "num_comments": 63,
          "subreddit": "ChronicPain",
          ...
        },
        "comments": [
          {
            "author": "user1",
            "body": "Comment text",
            "score": 10,
            "depth": 0,
            "replies": [
              {
                "author": "user2",
                "body": "Nested reply",
                "depth": 1,
                "replies": []
              }
            ]
          }
        ],
        "total_comments": 21
      }
    ],
    "count": 1
  }
}
```

---

### 4. **Reddit Complete Research** (Search → Scrape → Rank)

```bash
POST /dbas/api/reddit/complete-research/
Content-Type: application/json

{
  "market": "yoga for seniors with chronic pain",
  "num_results": 30,
  "top_n": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Complete Reddit research finished successfully",
  "data": {
    "market": "yoga for seniors with chronic pain",
    "total_urls_found": 30,
    "posts_scraped": 30,
    "posts_ranked": 10,
    "ranked_urls": [
      "https://reddit.com/r/yoga/...",
      "https://reddit.com/r/ChronicPain/..."
    ],
    "top_posts": [...]
  }
}
```

---

### 5. **Market Idea Expander**

```bash
POST /dbas/api/market-ideas/expand/
Content-Type: application/json

{
  "market_gaps_data": {
    /* Output from market gap generator (from complete-analysis endpoints) */
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Market ideas expanded successfully",
  "data": {
    "data": {
      "expanded_ideas": [...],
      "implementation_strategies": [...],
      "go_to_market_plans": [...]
    },
    "status": "success"
  }
}
```

---

## 🚀 Complete End-to-End Workflow

### Full Pipeline: Reddit → Pain Points → Market Gaps → Ideas

```bash
# Step 1: Get Reddit data (search, scrape, rank in one call)
curl -X POST "http://localhost:8000/dbas/api/reddit/complete-research/" \
  -H "Content-Type: application/json" \
  -d '{
    "market": "yoga accessibility for seniors",
    "num_results": 30,
    "top_n": 10
  }'

# Step 2: Extract pain points + Generate market gaps
curl -X POST "http://localhost:8000/dbas/api/pain-points/complete-analysis-reddit/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "posts": [/* Use posts from Step 1 */]
    }
  }'

# Step 3: Expand market ideas
curl -X POST "http://localhost:8000/dbas/api/market-ideas/expand/" \
  -H "Content-Type: application/json" \
  -d '{
    "market_gaps_data": {
      /* Use market_gaps from Step 2 */
    }
  }'
```

---

## 📊 Quick Summary

| Endpoint | Input | Output |
|----------|-------|--------|
| `/pain-points/complete-analysis-file/` | File (JSON/TXT) | Pain Points + Market Gaps |
| `/pain-points/complete-analysis-reddit/` | Reddit Data (JSON) | Pain Points + Market Gaps |
| `/reddit/scrape/` | URLs | Complete Post Data |
| `/reddit/complete-research/` | Market Query | Ranked Posts + URLs |
| `/market-ideas/expand/` | Market Gaps | Expanded Ideas |

---

## 🔗 API Documentation

Interactive docs: **http://localhost:8000/dbas/api/docs**

---

## ✨ Key Features

- ✅ **Combined endpoints** reduce API calls
- ✅ **Flexible input formats** (auto-detection)
- ✅ **Complete data extraction** (full Reddit content + comments)
- ✅ **End-to-end workflow** (3 steps from Reddit to market ideas)
- ✅ **Clean structure** (5 essential endpoints only)

