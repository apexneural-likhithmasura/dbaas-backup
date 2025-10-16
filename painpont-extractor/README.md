# Topics API - Complete Solution

FastAPI application for querying trending topics from PostgreSQL with year-wise filtering and top rankings.

---

## 🚀 Quick Start

### Start the API (Easiest Method)
```bash
cd /root/dbas/backend-final/painpont-extractor
./run_api.sh
```

**API will be available at:** http://localhost:8000  
**Interactive Docs:** http://localhost:8000/docs

---

## 📊 Features

✅ **PostgreSQL Integration** - 75 trending topics stored in database  
✅ **Year-wise Filtering** - Filter by 2, 10, or 15 years  
✅ **Top 6 Rankings** - Get highest growth topics per year  
✅ **Search Functionality** - Search by keyword in topics/descriptions  
✅ **Pagination Support** - Limit and offset parameters  
✅ **Health Monitoring** - Database connectivity checks  
✅ **Auto Documentation** - Interactive Swagger UI & ReDoc

---

## 🔌 API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/topics` | GET | Get all topics with filters | `curl "http://localhost:8000/topics?limit=5"` |
| **`/topics/top/{year}`** | **GET** | **🔥 Get top 6 by year** | **`curl "http://localhost:8000/topics/top/10"`** |
| `/topics/{id}` | GET | Get topic by ID | `curl "http://localhost:8000/topics/1"` |
| `/topics/stats` | GET | Get statistics | `curl "http://localhost:8000/topics/stats"` |
| `/health` | GET | Health check | `curl "http://localhost:8000/health"` |

---

## 💡 Usage Examples

### Get Top 6 Topics by Year (NEW!)
```bash
# 2 Years - Top trending topics
curl "http://localhost:8000/topics/top/2"

# 10 Years - Highest growth
curl "http://localhost:8000/topics/top/10"

# 15 Years - Long-term trends
curl "http://localhost:8000/topics/top/15"
```

**Response:**
```json
{
  "time_period": "10 Years",
  "time_period_requested": "10",
  "count": 6,
  "top_topics": [
    {
      "id": 26,
      "topic": "Ai image enhancer",
      "volume": "165K",
      "growth": "+9300%",
      "time_period": "10 Years"
    }
    // ... 5 more topics
  ]
}
```

### Filter Topics by Year
```bash
# Both formats work:
curl "http://localhost:8000/topics?time_period=2&limit=10"
curl "http://localhost:8000/topics?time_period=2%20Years&limit=10"
```

### Search Topics
```bash
curl "http://localhost:8000/topics?search=AI"
```

### Pagination
```bash
curl "http://localhost:8000/topics?limit=20&offset=0"
```

### Combined Filters
```bash
curl "http://localhost:8000/topics?time_period=10&search=AI&limit=5"
```

---

## 📈 Top Topics Results

### 2 Years (Short-term Trends)
1. **Pdrn toner** - +6600% growth
2. **Soursop bitters** - +725%
3. **Together AI** - +689%
4. **Shilajit honey** - +645%
5. **Lash Clusters** - +575%
6. **Wifi 7 router** - +428%

### 10 Years (Medium-term Growth)
1. **Ai image enhancer** - +9300% growth
2. **Preply** - +8800%
3. **Brightwheel** - +8600%
4. **Shilajit honey** - +8100%
5. **Lash Clusters** - +8000%
6. **20K PowerBank** - +7800%

### 15 Years (Long-term Evolution)
1. **Ai image enhancer** - +9300% growth
2. **Preply** - +8800%
3. **Brightwheel** - +8600%
4. **Shilajit honey** - +8100%
5. **Lash Clusters** - +8000%
6. **20K PowerBank** - +7800%

---

## 🛠️ Management Commands

### Start API
```bash
./run_api.sh
```

### Stop API
```bash
pkill -f pgmain.py
```

### View Logs
```bash
tail -f /tmp/api.log
```

### Check Status
```bash
ps aux | grep pgmain
curl http://localhost:8000/health
```

---

## ❌ Troubleshooting

### Error: "role 'root' does not exist"

**Cause:** Running API as root instead of postgres user.

**Solution:**
```bash
# Use the provided script (recommended)
./run_api.sh

# OR run manually as postgres user
sudo -u postgres python3 /tmp/pgmain.py
```

**For detailed troubleshooting, see:** `TROUBLESHOOTING.md`

---

## 📁 Project Structure

```
/root/dbas/backend-final/painpont-extractor/
├── pgmain.py                    # Main FastAPI application ⭐
├── run_api.sh                   # Easy start script 🚀
├── data.json                    # Source data (75 topics)
├── load_data_to_postgres.py     # Database setup script
├── test_api.py                  # Comprehensive test suite
├── API_DOCUMENTATION.md         # Full API documentation 📚
├── QUICK_START.md              # Quick reference guide
├── TROUBLESHOOTING.md          # Error solutions
├── DATABASE_INFO.md            # Database documentation
└── README.md                   # This file

/tmp/
├── pgmain.py                    # Runtime copy for postgres user
└── api.log                      # API logs
```

---

## 🗄️ Database Details

- **Database:** `topics_db`
- **User:** `postgres`
- **Table:** `topics`
- **Records:** 75 trending topics
- **Time Periods:** 2 Years, 10 Years, 15 Years (25 topics each)

**Schema:**
```sql
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(500) NOT NULL,
    volume VARCHAR(50),
    growth VARCHAR(50),
    description TEXT,
    url VARCHAR(1000),
    time_period VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Configuration

The API can be configured via environment variables:

```bash
export DB_NAME="topics_db"
export DB_USER="postgres"
export DB_PASSWORD=""           # Optional
export DB_HOST="localhost"
export DB_PORT="5432"
```

---

## 📖 Documentation

- **Interactive Swagger UI:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc
- **Full API Docs:** See `API_DOCUMENTATION.md`
- **Quick Reference:** See `QUICK_START.md`
- **Troubleshooting:** See `TROUBLESHOOTING.md`

---

## 🧪 Testing

Run the comprehensive test suite:
```bash
python3 test_api.py
```

Test the new top topics endpoint:
```bash
/tmp/test_top_endpoint.sh
```

---

## ✨ Key Features Explained

### Flexible Time Period Format
The API accepts both short and full formats:
- `2` or `2 Years` → Same result
- `10` or `10 Years` → Same result
- `15` or `15 Years` → Same result

### Automatic Growth Sorting
The top topics endpoint automatically sorts by growth percentage (highest first) using intelligent numeric parsing.

### Error Handling
The API provides helpful error messages and suggests solutions when issues occur.

---

## 📊 Statistics

```bash
curl "http://localhost:8000/topics/stats"
```

**Response:**
```json
{
  "total_topics": 75,
  "available_time_periods": ["2 Years", "10 Years", "15 Years"],
  "breakdown_by_time_period": [
    {"time_period": "2 Years", "count": 25},
    {"time_period": "10 Years", "count": 25},
    {"time_period": "15 Years", "count": 25}
  ]
}
```

---

## 🎯 Common Use Cases

1. **Trending Analysis** - Get top 6 topics for market research
2. **Year Comparison** - Compare trends across different time periods
3. **Keyword Research** - Search for specific topic categories
4. **Data Export** - Retrieve filtered data for analysis
5. **Real-time Monitoring** - Check health and connectivity

---

## 💻 Python Client Example

```python
import requests

# Get top 6 topics for 10 years
response = requests.get("http://localhost:8000/topics/top/10")
data = response.json()

print(f"Top {data['count']} topics for {data['time_period']}:")
for i, topic in enumerate(data['top_topics'], 1):
    print(f"{i}. {topic['topic']} - {topic['growth']}")
```

---

## 🔐 Security Notes

- Database uses peer authentication by default
- No hardcoded passwords in source code
- API runs as postgres user for security
- Environment variables for configuration

---

## 📝 Version Info

- **API Version:** 1.0.0
- **FastAPI:** 0.119.0
- **PostgreSQL:** 16
- **Python:** 3.12+

---

## 🆘 Getting Help

1. Check interactive documentation: `/docs`
2. Review troubleshooting guide: `TROUBLESHOOTING.md`
3. Check API logs: `tail -f /tmp/api.log`
4. Verify database: `sudo -u postgres psql -d topics_db`

---

## ✅ Quick Health Check

```bash
# 1. Check API is running
curl http://localhost:8000/health

# 2. Get statistics
curl http://localhost:8000/topics/stats

# 3. Test top topics endpoint
curl http://localhost:8000/topics/top/2
```

---

**🎉 You're all set! The API is ready to use.**

For detailed examples and advanced usage, see `API_DOCUMENTATION.md`
