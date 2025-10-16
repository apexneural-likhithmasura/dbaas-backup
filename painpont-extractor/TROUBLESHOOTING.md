# Troubleshooting Guide - Topics API

## Common Error: "role 'root' does not exist"

### Error Message
```json
{
  "detail": "Database connection error: connection to server on socket \"/var/run/postgresql/.s.PGSQL.5432\" failed: FATAL: role \"root\" does not exist\n"
}
```

### Cause
This error occurs when you try to run the API as the `root` user (or any user other than `postgres`) without proper PostgreSQL authentication configured.

PostgreSQL uses **peer authentication** by default on Unix sockets, which means:
- The database username must match the system username
- If you run as `root`, PostgreSQL looks for a database role named `root`
- Since only `postgres` role exists, the connection fails

---

## Solutions

### ✅ Solution 1: Use the Run Script (Recommended)

Use the provided script that handles everything automatically:

```bash
cd /root/dbas/backend-final/painpont-extractor
./run_api.sh
```

This script:
- Copies files to `/tmp` where postgres user can access them
- Stops any existing API instances
- Starts the API as the postgres user
- Shows status and helpful links

---

### ✅ Solution 2: Run Manually as Postgres User

```bash
# Copy to /tmp
cp /root/dbas/backend-final/painpont-extractor/pgmain.py /tmp/

# Run as postgres user
cd /tmp
sudo -u postgres python3 pgmain.py
```

---

### ✅ Solution 3: Configure Password Authentication (Advanced)

If you need to run as root or another user, configure PostgreSQL password authentication:

#### Step 1: Set password for postgres user
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"
```

#### Step 2: Update pg_hba.conf
```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Change this line:
```
local   all             postgres                                peer
```

To:
```
local   all             postgres                                md5
```

#### Step 3: Restart PostgreSQL
```bash
sudo service postgresql restart
```

#### Step 4: Run API with password
```bash
export DB_PASSWORD="your_password"
python3 pgmain.py
```

Or set it in the environment:
```bash
DB_PASSWORD="your_password" python3 pgmain.py
```

---

## Other Common Issues

### Issue: Port 8000 Already in Use

**Error:**
```
ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```

**Solution:**
```bash
# Find and kill the process using port 8000
pkill -f pgmain.py

# Or use lsof to find the process
lsof -ti:8000 | xargs kill -9

# Then restart the API
./run_api.sh
```

---

### Issue: Can't Access /root Directory as Postgres User

**Error:**
```
Permission denied: '/root/dbas/backend-final/painpont-extractor/pgmain.py'
```

**Solution:**
Always copy files to `/tmp` first:
```bash
cp /root/dbas/backend-final/painpont-extractor/pgmain.py /tmp/
cd /tmp
sudo -u postgres python3 pgmain.py
```

---

### Issue: Database Not Found

**Error:**
```json
{
  "detail": "Database connection error: FATAL: database \"topics_db\" does not exist"
}
```

**Solution:**
Run the database setup script:
```bash
cd /tmp
sudo -u postgres python3 load_data_to_postgres.py
```

---

### Issue: Python Package Missing

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
Install required packages:
```bash
pip3 install fastapi uvicorn --break-system-packages
# or
apt-get install -y python3-psycopg2
```

---

## Verifying the API is Running

### Check Process
```bash
ps aux | grep pgmain
```

Expected output:
```
postgres   XXXX  X.X  X.X  XXXXX XXXXX ?  S  HH:MM   X:XX python3 pgmain.py
```

### Check Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "API is running and database is accessible"
}
```

### Check Logs
```bash
tail -f /tmp/api.log
```

---

## Quick Diagnostic Commands

```bash
# 1. Check PostgreSQL is running
sudo service postgresql status

# 2. Check if database exists
sudo -u postgres psql -l | grep topics_db

# 3. Check if API port is available
lsof -i:8000

# 4. Test database connection directly
sudo -u postgres psql -d topics_db -c "SELECT COUNT(*) FROM topics;"

# 5. Check API process
ps aux | grep pgmain | grep -v grep
```

---

## Environment Variables

You can configure the API using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_NAME` | `topics_db` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `` | Database password (optional) |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |

Example:
```bash
export DB_NAME="topics_db"
export DB_USER="postgres"
export DB_PASSWORD="mypassword"
python3 pgmain.py
```

---

## Still Having Issues?

1. **Check the logs:** `tail -f /tmp/api.log`
2. **Test database connection:** `sudo -u postgres psql -d topics_db`
3. **Verify PostgreSQL is running:** `sudo service postgresql status`
4. **Check file permissions:** `ls -la /tmp/pgmain.py`

---

## Best Practices

✅ **DO:**
- Use the `run_api.sh` script for easy startup
- Run as postgres user for peer authentication
- Keep API files in `/tmp` for accessibility
- Check logs when errors occur

❌ **DON'T:**
- Run as root without password authentication
- Modify PostgreSQL config unless necessary
- Hardcode passwords in scripts
- Run multiple API instances on same port

---

**Need Help?** Check the API documentation at `/docs` endpoint or review `API_DOCUMENTATION.md`

