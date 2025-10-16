#!/bin/bash
# Simple script to start the Topics API with your database credentials

echo "=========================================="
echo "  Starting Topics API with Database Credentials"
echo "=========================================="
echo ""

# Stop any existing instances
echo "Stopping existing API instances..."
pkill -9 -f pgmain.py 2>/dev/null || true
sleep 2

# Copy latest version
echo "Copying API to /tmp..."
cp /root/dbas/backend-final/painpont-extractor/pgmain.py /tmp/pgmain.py

# Start the API (now works as any user with built-in password)
echo "Starting API with database credentials..."
cd /tmp
python3 pgmain.py &

sleep 3

# Check if running
if ps aux | grep -v grep | grep "pgmain.py" > /dev/null; then
    echo ""
    echo "✅ API Started Successfully!"
    echo ""
    echo "🌐 API URL: http://localhost:8000"
    echo "📚 Interactive Docs: http://localhost:8000/docs"
    echo "📖 ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "🔍 Test the top topics endpoint:"
    echo "curl \"http://localhost:8000/topics/top/15\""
    echo ""
    echo "🛑 To stop: pkill -f pgmain.py"
    echo "📋 To view logs: tail -f /tmp/api.log"
    echo ""
else
    echo ""
    echo "❌ Failed to start API. Check for errors above."
    echo ""
fi
