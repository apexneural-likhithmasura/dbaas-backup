#!/bin/bash
# Script to run the Topics API
# This ensures the API runs with proper PostgreSQL permissions

echo "========================================"
echo "  Starting Topics API Server"
echo "========================================"
echo ""

# Copy latest version to /tmp
echo "Copying API to /tmp directory..."
cp /root/dbas/backend-final/painpont-extractor/pgmain.py /tmp/pgmain.py
chmod 755 /tmp/pgmain.py

# Stop any existing instances
echo "Stopping existing API instances..."
pkill -9 -f "pgmain.py" 2>/dev/null || true
sleep 2

# Start the API as postgres user
echo "Starting API as postgres user..."
cd /tmp
sudo -u postgres python3 pgmain.py &

sleep 3

# Check if running
if ps aux | grep -v grep | grep "pgmain.py" > /dev/null; then
    echo ""
    echo "✅ API Started Successfully!"
    echo ""
    echo "API URL: http://localhost:8000"
    echo "Interactive Docs: http://localhost:8000/docs"
    echo "ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "To stop the API: pkill -f pgmain.py"
    echo "To view logs: tail -f /tmp/api.log"
    echo ""
else
    echo ""
    echo "❌ Failed to start API. Check /tmp/api.log for errors"
    echo ""
fi

