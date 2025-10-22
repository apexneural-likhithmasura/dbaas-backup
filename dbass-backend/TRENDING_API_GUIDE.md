# Trending Topics API Guide

## Overview

The Trending Topics API provides endpoints to access and analyze trending topics data stored in a PostgreSQL database. This module is integrated into the existing Pain Point & Market Gap Analyzer API.

## Configuration

Add the following environment variables to your `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trending_topics
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_SCHEMA=public
```

## Database Schema

The API expects a table named `trending_topics` with the following structure:

```sql
CREATE TABLE public.trending_topics (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(500) NOT NULL,
    volume VARCHAR(50) NOT NULL,
    growth VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    url TEXT NOT NULL,
    time_period VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

All endpoints are prefixed with: `/dbas/api/trending`

### 1. Get Top 6 Trending Topics

**Endpoint:** `GET /dbas/api/trending/top-trending`

Returns the top 6 trending topics sorted by growth percentage.

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved top 6 trending topics",
  "data": [
    {
      "id": 1,
      "topic": "Example Topic",
      "volume": "50K-100K",
      "growth": "+1200%",
      "description": "Description of the trending topic",
      "url": "https://example.com",
      "time_period": "October 2024",
      "created_at": "2024-10-15T10:30:00"
    }
  ],
  "count": 6,
  "timestamp": "2025-10-22T10:30:00"
}
```

### 2. Get All Trending Topics

**Endpoint:** `GET /dbas/api/trending/all`

Returns all trending topics with optional pagination.

**Query Parameters:**
- `limit` (optional): Maximum number of topics to return (1-100)
- `offset` (optional): Number of topics to skip (default: 0)

**Example:**
```
GET /dbas/api/trending/all?limit=10&offset=0
```

### 3. Search Trending Topics

**Endpoint:** `GET /dbas/api/trending/search`

Search topics by name or description.

**Query Parameters:**
- `q` (required): Search query string
- `limit` (optional): Maximum number of results (1-100)

**Example:**
```
GET /dbas/api/trending/search?q=technology&limit=20
```

### 4. Get Topic by ID

**Endpoint:** `GET /dbas/api/trending/{topic_id}`

Retrieve a specific trending topic by its ID.

**Example:**
```
GET /dbas/api/trending/42
```

### 5. Get Statistics

**Endpoint:** `GET /dbas/api/trending/stats/summary`

Get various statistics about trending topics data.

**Response:**
```json
{
  "status": "success",
  "message": "Statistics retrieved successfully",
  "data": {
    "total_topics": 150,
    "unique_time_periods": 5,
    "average_growth": 456.78,
    "time_period_breakdown": [
      {
        "time_period": "October 2024",
        "count": 30
      }
    ]
  }
}
```

### 6. Health Check

**Endpoint:** `GET /dbas/api/trending/health/check`

Check database connection and table availability.

**Response:**
```json
{
  "status": "success",
  "message": "Service is healthy",
  "data": {
    "database_connected": true,
    "table_exists": true,
    "service_status": "healthy"
  }
}
```

## Architecture

### File Structure

```
app/
├── api/
│   └── routes/
│       └── trending_routes.py       # API endpoints
├── db/
│   └── database.py                  # Database connection manager
├── models/
│   └── trending_models.py           # Pydantic models
├── services/
│   └── trending_service.py          # Business logic
└── core/
    └── config.py                    # Configuration (updated)
```

### Components

1. **Database Manager** (`app/db/database.py`)
   - Handles PostgreSQL connections
   - Provides context managers for safe resource management
   - Uses `psycopg2` for database operations

2. **Models** (`app/models/trending_models.py`)
   - `TrendingTopicBase`: Base model with validation
   - `TrendingTopic`: Complete model with ID and timestamps
   - `TrendingTopicResponse`: API response wrapper

3. **Service Layer** (`app/services/trending_service.py`)
   - Business logic for all trending topics operations
   - Database query handling
   - Data transformation and sorting

4. **Routes** (`app/api/routes/trending_routes.py`)
   - RESTful API endpoints
   - Request validation
   - Error handling

## Usage Examples

### Python (using requests)

```python
import requests

# Get top trending topics
response = requests.get('http://localhost:8000/dbas/api/trending/top-trending')
data = response.json()
print(f"Found {data['count']} trending topics")

# Search for specific topics
response = requests.get(
    'http://localhost:8000/dbas/api/trending/search',
    params={'q': 'AI', 'limit': 5}
)
topics = response.json()['data']
```

### cURL

```bash
# Get top trending topics
curl http://localhost:8000/dbas/api/trending/top-trending

# Search topics
curl "http://localhost:8000/dbas/api/trending/search?q=technology&limit=10"

# Get specific topic
curl http://localhost:8000/dbas/api/trending/123

# Health check
curl http://localhost:8000/dbas/api/trending/health/check
```

### JavaScript (using fetch)

```javascript
// Get top trending topics
fetch('http://localhost:8000/dbas/api/trending/top-trending')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} trending topics`);
    data.data.forEach(topic => {
      console.log(`${topic.topic}: ${topic.growth} growth`);
    });
  });
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad request (validation error)
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable (database connection issue)

Error responses follow this format:

```json
{
  "status": "error",
  "message": "Error description",
  "timestamp": "2025-10-22T10:30:00"
}
```

## Testing

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/dbas/api/docs`
- ReDoc: `http://localhost:8000/dbas/api/redoc`

## Dependencies

The following packages are required (already in `requirements.txt`):

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `psycopg2-binary`: PostgreSQL adapter
- `pydantic`: Data validation
- `pydantic-settings`: Settings management
- `python-dotenv`: Environment variable loading

## Troubleshooting

### Database Connection Issues

1. Verify database credentials in `.env` file
2. Check if PostgreSQL is running
3. Ensure the database exists
4. Verify network connectivity

### Table Not Found

Create the table using the SQL schema provided above, or check the health endpoint:
```bash
curl http://localhost:8000/dbas/api/trending/health/check
```

### No Data Returned

Verify that data exists in the table:
```sql
SELECT COUNT(*) FROM public.trending_topics;
```

## Logging

The module uses Python's standard logging. Logs are output to:
- Console (stdout)
- `app.log` file (in production mode)

Log levels can be configured via the `LOG_LEVEL` environment variable.

