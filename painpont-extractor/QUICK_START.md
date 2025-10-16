# Quick Start Guide - Topics API

## 🚀 Running the API

```bash
cd /tmp
sudo -u postgres python3 pgmain.py
```

Server starts at: **http://localhost:8000**

---

## 📚 Quick Reference

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /topics` | Get all topics | `curl "http://localhost:8000/topics?limit=5"` |
| `GET /topics/top/{year}` | **🔥 Get top 6 by year** | `curl "http://localhost:8000/topics/top/2"` |
| `GET /topics/stats` | Get statistics | `curl "http://localhost:8000/topics/stats"` |
| `GET /topics/{id}` | Get topic by ID | `curl "http://localhost:8000/topics/1"` |
| `GET /health` | Health check | `curl "http://localhost:8000/health"` |

---

## 🔍 Common Queries

### 🔥 Get Top 6 Topics by Year (NEW!)
```bash
# Get top 6 trending topics for 2 years
curl "http://localhost:8000/topics/top/2"

# Get top 6 for 10 years (both formats work)
curl "http://localhost:8000/topics/top/10"
curl "http://localhost:8000/topics/top/10%20Years"

# Get top 6 for 15 years
curl "http://localhost:8000/topics/top/15"
```

### Filter by Year (Flexible Format)
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

## 📊 Available Time Periods
- `2` or `2 Years` → 25 topics
- `10` or `10 Years` → 25 topics  
- `15` or `15 Years` → 25 topics

**Total Topics:** 75

---

## 🛠️ Management Commands

### Start Server
```bash
cd /tmp && sudo -u postgres python3 pgmain.py
```

### Start in Background
```bash
cd /tmp && nohup sudo -u postgres python3 pgmain.py > /tmp/api.log 2>&1 &
```

### Check if Running
```bash
ps aux | grep pgmain
```

### Stop Server
```bash
pkill -f "python3 pgmain.py"
```

### View Logs
```bash
tail -f /tmp/api.log
```

---

## 📝 Response Format

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
      "url": "https://explodingtopics.com/topic/...",
      "time_period": "10 Years",
      "created_at": "2025-10-15T06:30:16.374026"
    }
  ]
}
```

---

## 🧪 Testing

```bash
python3 /root/dbas/backend-final/painpont-extractor/test_api.py
```

---

## 📦 Files Structure

```
/root/dbas/backend-final/painpont-extractor/
├── pgmain.py                    # FastAPI application
├── test_api.py                  # Test suite
├── load_data_to_postgres.py     # Database setup
├── data.json                    # Source data
├── API_DOCUMENTATION.md         # Full API docs
├── DATABASE_INFO.md             # Database docs
└── QUICK_START.md              # This file

/tmp/
├── pgmain.py                    # Copy for postgres user
└── api.log                      # API logs
```

---

## 💡 Tips

1. **Use `/docs`** for interactive testing
2. **Check `/health`** to verify database connection
3. **Use `/stats`** to see data distribution
4. **Time period is flexible** - use `2` or `2 Years`
5. **Combine filters** for powerful queries

---

For complete documentation, see **API_DOCUMENTATION.md**

