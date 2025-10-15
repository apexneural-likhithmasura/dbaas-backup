# 🎯 API Endpoints - Essential Only (Cleaned Up)

## ✅ 4 Essential Endpoints

### 1. **Pain Point + Market Gap Analysis** (Combined)

#### 📁 File Input (JSON/TXT)
```bash
POST /dbas/api/pain-points/complete-analysis-file/
Content-Type: multipart/form-data
Body: files=@data.json
```

#### 📝 Reddit Data Input
```bash
POST /dbas/api/pain-points/complete-analysis-reddit/
Content-Type: application/json
Body: {
  "post": { "title": "...", "selftext": "..." },
  "comments": [...]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pain_points": { /* Full pain point analysis */ },
    "market_gaps": { /* Market gap solutions */ }
  }
}
```

---

### 2. **Reddit Scraping**

```bash
POST /dbas/api/reddit/scrape/
Content-Type: application/json
Body: {
  "urls": ["https://www.reddit.com/r/yoga/comments/..."]
}
```

**Response:** Complete post data with full content + nested comments

---

### 3. **Reddit Complete Research**

```bash
POST /dbas/api/reddit/complete-research/
Content-Type: application/json
Body: {
  "market": "yoga for seniors with chronic pain",
  "num_results": 30,
  "top_n": 10
}
```

**Response:** Search → Scrape → Rank (includes `ranked_urls`)

---

### 4. **Market Idea Expander**

```bash
POST /dbas/api/market-ideas/expand/
Content-Type: application/json
Body: {
  "market_gaps_data": { /* From complete-analysis */ }
}
```

**Response:** Detailed market strategies and implementation

---

## 🚀 Complete Workflow (3 Steps)

```
1. POST /reddit/complete-research/
   ↓ Get ranked Reddit posts

2. POST /pain-points/complete-analysis-reddit/
   ↓ Get pain_points + market_gaps

3. POST /market-ideas/expand/
   ↓ Get detailed implementation strategies
```

---

## 📚 Documentation

Interactive API docs: **http://localhost:8000/dbas/api/docs**

---

## ✨ Cleanup Summary

- **Before:** 13 endpoints
- **After:** 4 essential endpoints
- **Benefit:** Clearer structure, fewer API calls, easier to use

