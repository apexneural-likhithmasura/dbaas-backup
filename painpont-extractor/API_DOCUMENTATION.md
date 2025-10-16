# Topics API Documentation

## Overview

FastAPI application for querying trending topics data from PostgreSQL database with advanced filtering capabilities.

## Base URL
```
http://localhost:8000
```

## API Features

- ✅ Get all topics with pagination
- ✅ Filter by time period (flexible format: `2`, `10`, `15` or `2 Years`, `10 Years`, `15 Years`)
- ✅ Search topics by keyword
- ✅ Pagination support (limit & offset)
- ✅ Database health check
- ✅ Statistics endpoint
- ✅ Auto-generated interactive documentation

---

## Endpoints

### 1. Root Endpoint
**GET** `/`

Returns API information and available endpoints.

**Example:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Topics API",
  "version": "1.0.0",
  "endpoints": {
    "/topics": "Get all topics with optional filtering",
    "/topics/stats": "Get statistics about topics",
    "/docs": "API documentation"
  }
}
```

---

### 2. Get Topics (Main Endpoint)
**GET** `/topics`

Retrieve topics with optional filtering and pagination.

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `time_period` | string | No | Filter by time period. Accepts: `2`, `10`, `15` or `2 Years`, `10 Years`, `15 Years` | `10` or `10 Years` |
| `limit` | integer | No | Maximum number of results (1-1000) | `10` |
| `offset` | integer | No | Number of records to skip (for pagination) | `0` |
| `search` | string | No | Search keyword in topic name or description | `AI` |

#### Examples

**Get all topics (limit 5):**
```bash
curl "http://localhost:8000/topics?limit=5"
```

**Filter by time period (flexible format):**
```bash
# Both formats work:
curl "http://localhost:8000/topics?time_period=10&limit=5"
curl "http://localhost:8000/topics?time_period=10%20Years&limit=5"
```

**Search for AI-related topics:**
```bash
curl "http://localhost:8000/topics?search=AI"
```

**Pagination example:**
```bash
curl "http://localhost:8000/topics?limit=10&offset=20"
```

**Combined filters:**
```bash
curl "http://localhost:8000/topics?time_period=2&search=skincare&limit=5"
```

#### Response Format

```json
{
  "total": 25,
  "time_period_filter": "10",
  "data": [
    {
      "id": 26,
      "topic": "Ai image enhancer",
      "volume": "165K",
      "growth": "+9300%",
      "description": "Advanced software solutions...",
      "url": "https://explodingtopics.com/topic/ai-image-enhancer",
      "time_period": "10 Years",
      "created_at": "2025-10-15T06:30:16.374026"
    }
  ]
}
```

---

### 3. Get Topic by ID
**GET** `/topics/{topic_id}`

Retrieve a specific topic by its ID.

**Example:**
```bash
curl http://localhost:8000/topics/1
```

**Response:**
```json
{
  "id": 1,
  "topic": "Pdrn toner",
  "volume": "880",
  "growth": "+6600%",
  "description": "An anti-aging skincare product...",
  "url": "https://explodingtopics.com/topic/pdrn-toner-rBqL9YyX",
  "time_period": "2 Years",
  "created_at": "2025-10-15T06:30:16.374026"
}
```

---

### 4. Get Top 6 Topics by Year (NEW)
**GET** `/topics/top/{time_period}`

Get the top 6 topics for a specific time period, sorted by highest growth percentage.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `time_period` | string | Yes | Time period: `2`, `10`, `15` or `2 Years`, `10 Years`, `15 Years` |

**Examples:**

```bash
# Get top 6 topics for 2 years (both formats work)
curl "http://localhost:8000/topics/top/2"
curl "http://localhost:8000/topics/top/2%20Years"

# Get top 6 topics for 10 years
curl "http://localhost:8000/topics/top/10"

# Get top 6 topics for 15 years
curl "http://localhost:8000/topics/top/15%20Years"
```

**Response:**
```json
{
  "time_period": "2 Years",
  "time_period_requested": "2",
  "count": 6,
  "top_topics": [
    {
      "id": 1,
      "topic": "Pdrn toner",
      "volume": "880",
      "growth": "+6600%",
      "description": "An anti-aging skincare product...",
      "url": "https://explodingtopics.com/topic/pdrn-toner-rBqL9YyX",
      "time_period": "2 Years",
      "created_at": "2025-10-15T06:30:16.374026"
    },
    {
      "id": 2,
      "topic": "Soursop bitters",
      "volume": "110K",
      "growth": "+725%",
      "description": "Soursop bitters is a herbal supplement...",
      "url": "https://explodingtopics.com/topic/soursop-bitters",
      "time_period": "2 Years",
      "created_at": "2025-10-15T06:30:16.374026"
    }
    // ... 4 more topics
  ]
}
```

**Top Topics by Time Period:**

**2 Years:**
1. Pdrn toner (+6600%)
2. Soursop bitters (+725%)
3. Together AI (+689%)
4. Shilajit honey (+645%)
5. Lash Clusters (+575%)
6. Wifi 7 router (+428%)

**10 Years:**
1. Ai image enhancer (+9300%)
2. Preply (+8800%)
3. Brightwheel (+8600%)
4. Shilajit honey (+8100%)
5. Lash Clusters (+8000%)
6. 20K PowerBank (+7800%)

**15 Years:**
1. Ai image enhancer (+9300%)
2. Preply (+8800%)
3. Brightwheel (+8600%)
4. Shilajit honey (+8100%)
5. Lash Clusters (+8000%)
6. 20K PowerBank (+7800%)

---

### 6. Get Statistics
**GET** `/topics/stats`

Get overall statistics about the topics database.

**Example:**
```bash
curl http://localhost:8000/topics/stats
```

**Response:**
```json
{
  "total_topics": 75,
  "available_time_periods": [
    "10 Years",
    "15 Years",
    "2 Years"
  ],
  "breakdown_by_time_period": [
    {
      "time_period": "10 Years",
      "count": 25
    },
    {
      "time_period": "15 Years",
      "count": 25
    },
    {
      "time_period": "2 Years",
      "count": 25
    }
  ]
}
```

---

### 7. Health Check
**GET** `/health`

Check API and database connectivity status.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response (Healthy):**
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "API is running and database is accessible"
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "Connection error details..."
}
```

---

## Database Configuration

The API uses PostgreSQL with the following configuration:

```python
DATABASE_URL = "postgresql://postgres:password@localhost:5432/topics_db"
DB_NAME = "topics_db"
```

**Database Schema:**
- Table: `topics`
- Fields: `id`, `topic`, `volume`, `growth`, `description`, `url`, `time_period`, `created_at`

---

## Running the API

### Start the Server

```bash
# From /tmp directory (where postgres user has access)
cd /tmp
sudo -u postgres python3 pgmain.py
```

The server will start on `http://0.0.0.0:8000`

### Alternative: Run in Background

```bash
cd /tmp
nohup sudo -u postgres python3 pgmain.py > /tmp/api.log 2>&1 &
```

### Check if Running

```bash
ps aux | grep pgmain
```

### Stop the Server

```bash
pkill -f "python3 pgmain.py"
```

---

## Interactive API Documentation

FastAPI provides auto-generated interactive documentation:

### Swagger UI
**URL:** `http://localhost:8000/docs`

Features:
- Browse all endpoints
- Try API calls directly from browser
- See request/response schemas
- Test different parameters

### ReDoc
**URL:** `http://localhost:8000/redoc`

Alternative documentation interface with a different layout.

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get topics filtered by time period
response = requests.get(f"{BASE_URL}/topics", params={
    "time_period": "10",  # Flexible: can be "10" or "10 Years"
    "limit": 10,
    "offset": 0
})

data = response.json()
print(f"Total topics: {data['total']}")

for topic in data['data']:
    print(f"- {topic['topic']} | Growth: {topic['growth']}")

# Search for specific topics
response = requests.get(f"{BASE_URL}/topics", params={
    "search": "AI",
    "time_period": "2"
})

ai_topics = response.json()
print(f"Found {ai_topics['total']} AI-related topics")
```

---

## Common Use Cases

### 1. Get trending topics for the last 2 years
```bash
curl "http://localhost:8000/topics?time_period=2&limit=10"
```

### 2. Paginate through all topics
```bash
# Page 1
curl "http://localhost:8000/topics?limit=20&offset=0"

# Page 2
curl "http://localhost:8000/topics?limit=20&offset=20"

# Page 3
curl "http://localhost:8000/topics?limit=20&offset=40"
```

### 3. Search and filter combination
```bash
curl "http://localhost:8000/topics?time_period=10&search=AI&limit=5"
```

### 4. Get topic details by ID
```bash
curl "http://localhost:8000/topics/15"
```

---

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful request
- `404 Not Found` - Topic ID not found
- `422 Unprocessable Entity` - Invalid parameters
- `500 Internal Server Error` - Database or server error
- `503 Service Unavailable` - Database connection failed

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Time Period Normalization

The API automatically normalizes time period inputs for user convenience:

| User Input | Normalized To | Results |
|------------|---------------|---------|
| `2` | `2 Years` | ✅ Returns 2-year topics |
| `10` | `10 Years` | ✅ Returns 10-year topics |
| `15` | `15 Years` | ✅ Returns 15-year topics |
| `2 Years` | `2 Years` | ✅ Returns 2-year topics |
| `10 Years` | `10 Years` | ✅ Returns 10-year topics |

---

## Performance Tips

1. **Use pagination** for large result sets:
   ```bash
   curl "http://localhost:8000/topics?limit=50&offset=0"
   ```

2. **Filter early** - Combine time_period and search to reduce result set:
   ```bash
   curl "http://localhost:8000/topics?time_period=2&search=tech"
   ```

3. **Check stats** first to understand data distribution:
   ```bash
   curl "http://localhost:8000/topics/stats"
   ```

---

## Testing

Run the included test suite:

```bash
cd /root/dbas/backend-final/painpont-extractor
python3 test_api.py
```

This will test all endpoints and display results.

---

## Files

- `pgmain.py` - Main FastAPI application
- `test_api.py` - Comprehensive test suite
- `load_data_to_postgres.py` - Database setup script
- `DATABASE_INFO.md` - Database documentation
- `API_DOCUMENTATION.md` - This file

---

## Support

For issues or questions:
1. Check the interactive docs at `/docs`
2. Verify database connection with `/health`
3. Check API logs in `/tmp/api.log`
4. Review PostgreSQL logs if database issues occur

---

**Last Updated:** October 15, 2025
**API Version:** 1.0.0
**Framework:** FastAPI 0.119.0
**Database:** PostgreSQL 16

