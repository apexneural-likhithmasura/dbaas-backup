#!/bin/bash
# Script to set up password authentication for PostgreSQL
# This allows running the API as any user (including root)

echo "=========================================="
echo "  PostgreSQL Password Authentication Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "This script will configure PostgreSQL to allow password authentication."
echo "After setup, you can run the API as any user by setting DB_PASSWORD."
echo ""

read -p "Enter a password for the 'postgres' user (or press Enter for default 'password'): " POSTGRES_PASSWORD
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}

echo ""
echo "Setting up password authentication..."

# Step 1: Set password for postgres user
echo "1. Setting password for postgres user..."
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '$POSTGRES_PASSWORD';"
if [ $? -eq 0 ]; then
    echo "   ✅ Password set successfully"
else
    echo "   ❌ Failed to set password"
    exit 1
fi

# Step 2: Backup original pg_hba.conf
echo ""
echo "2. Backing up pg_hba.conf..."
sudo cp /etc/postgresql/16/main/pg_hba.conf /etc/postgresql/16/main/pg_hba.conf.backup
echo "   ✅ Backup created at /etc/postgresql/16/main/pg_hba.conf.backup"

# Step 3: Update pg_hba.conf to allow password authentication
echo ""
echo "3. Updating pg_hba.conf for password authentication..."

# Create a temporary file with updated configuration
cat > /tmp/pg_hba_update.conf << EOF
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer
local   all             postgres                                md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5
EOF

# Replace the relevant lines in pg_hba.conf
sudo sed -i '/^local.*all.*postgres.*peer/c\local   all             postgres                                md5' /etc/postgresql/16/main/pg_hba.conf
sudo sed -i '/^host.*all.*127.0.0.1\/32.*trust/c\host    all             all             127.0.0.1/32            md5' /etc/postgresql/16/main/pg_hba.conf
sudo sed -i '/^host.*all.*::1\/128.*trust/c\host    all             all             ::1/128                 md5' /etc/postgresql/16/main/pg_hba.conf

echo "   ✅ pg_hba.conf updated"

# Step 4: Restart PostgreSQL
echo ""
echo "4. Restarting PostgreSQL service..."
sudo service postgresql restart
if [ $? -eq 0 ]; then
    echo "   ✅ PostgreSQL restarted successfully"
else
    echo "   ❌ Failed to restart PostgreSQL"
    exit 1
fi

# Step 5: Test connection
echo ""
echo "5. Testing password authentication..."
echo "   Testing connection with password..."
PGPASSWORD="$POSTGRES_PASSWORD" psql -h localhost -U postgres -d postgres -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Password authentication working"
else
    echo "   ❌ Password authentication failed"
    echo "   You may need to check the pg_hba.conf configuration"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Setup Complete! ✅"
echo "=========================================="
echo ""
echo "Now you can run the API as any user:"
echo ""
echo "Method 1: Set environment variable"
echo "export DB_PASSWORD=\"$POSTGRES_PASSWORD\""
echo "python3 pgmain.py"
echo ""
echo "Method 2: Run with inline variable"
echo "DB_PASSWORD=\"$POSTGRES_PASSWORD\" python3 pgmain.py"
echo ""
echo "Method 3: Update the script directly"
echo "# Edit pgmain.py and set:"
echo "DB_PASSWORD = \"$POSTGRES_PASSWORD\""
echo ""
echo "To revert to peer authentication:"
echo "sudo cp /etc/postgresql/16/main/pg_hba.conf.backup /etc/postgresql/16/main/pg_hba.conf"
echo "sudo service postgresql restart"
echo ""
echo "Password for postgres user: $POSTGRES_PASSWORD"
echo ""

# Create a test script
cat > /tmp/test_password_auth.py << 'EOF'
#!/usr/bin/env python3
import psycopg2
import os

# Test password authentication
password = os.getenv('DB_PASSWORD', 'password')
try:
    conn = psycopg2.connect(
        dbname='topics_db',
        user='postgres',
        password=password,
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM topics")
    count = cursor.fetchone()[0]
    print(f"✅ Connection successful! Found {count} topics in database.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF

chmod +x /tmp/test_password_auth.py

echo "Test password authentication:"
echo "DB_PASSWORD=\"$POSTGRES_PASSWORD\" python3 /tmp/test_password_auth.py"
