# 🧪 Testing complete-analysis-reddit Endpoint

## ✅ The endpoint NOW accepts 3 input formats:

### Format 1: Direct Post Data (Recommended)
```json
{
  "post": {
    "title": "Yoga is inaccessible...",
    "selftext": "Post content here...",
    "author": "username",
    "score": 129
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

### Format 2: Wrapped in "data" (From /reddit/scrape/)
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

### Format 3: Array of posts
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

## 🧪 Quick Test

```bash
curl -X POST "http://localhost:8000/dbas/api/pain-points/complete-analysis-reddit/" \
  -H "Content-Type: application/json" \
  -d '{
    "post": {
      "title": "Test post about chronic pain",
      "selftext": "I have been struggling with chronic pain for years. Yoga makes it worse.",
      "author": "testuser",
      "score": 10
    },
    "comments": [
      {
        "author": "helper",
        "body": "Have you tried physical therapy?",
        "score": 5,
        "depth": 0,
        "replies": []
      }
    ],
    "total_comments": 1
  }'
```

## ✅ Expected Response

```json
{
  "success": true,
  "message": "Complete analysis pipeline executed successfully from Reddit data",
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
        "frameworks_applied": [...]
      },
      "status": "success"
    }
  }
}
```

## ❌ If you get your input echoed back:

The endpoint couldn't process the data. Check:
1. Is the JSON valid?
2. Does it have a "post" key?
3. Is the API key configured?

