#!/usr/bin/env python3
"""
Script to load JSON data into PostgreSQL database
"""
import json
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database configuration
DB_NAME = "topics_db"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server as postgres user
        conn = psycopg2.connect(
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_NAME)
            ))
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def create_table():
    """Create the topics table"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        # Drop table if exists (for clean slate)
        cursor.execute("DROP TABLE IF EXISTS topics")
        
        # Create table
        create_table_query = """
        CREATE TABLE topics (
            id SERIAL PRIMARY KEY,
            topic VARCHAR(500) NOT NULL,
            volume VARCHAR(50),
            growth VARCHAR(50),
            description TEXT,
            url VARCHAR(1000),
            time_period VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table 'topics' created successfully")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

def load_json_data(json_file_path):
    """Load data from JSON file into PostgreSQL"""
    try:
        # Read JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} records from JSON file")
        
        # Connect to database
        conn = psycopg2.connect(
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        # Insert data
        insert_query = """
        INSERT INTO topics (topic, volume, growth, description, url, time_period)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        for item in data:
            cursor.execute(insert_query, (
                item.get('topic', ''),
                item.get('volume', ''),
                item.get('growth', ''),
                item.get('description', ''),
                item.get('url', ''),
                item.get('time_period', '')
            ))
            inserted_count += 1
        
        conn.commit()
        print(f"Successfully inserted {inserted_count} records into database")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM topics")
        count = cursor.fetchone()[0]
        print(f"Total records in database: {count}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def display_sample_data():
    """Display sample data from the database"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, topic, volume, growth, time_period FROM topics LIMIT 5")
        rows = cursor.fetchall()
        
        print("\n=== Sample Data (First 5 Records) ===")
        print(f"{'ID':<5} {'Topic':<30} {'Volume':<10} {'Growth':<10} {'Period':<15}")
        print("-" * 75)
        for row in rows:
            print(f"{row[0]:<5} {row[1][:28]:<30} {row[2]:<10} {row[3]:<10} {row[4]:<15}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error displaying data: {e}")

def main():
    print("=== PostgreSQL Data Loader ===\n")
    
    # Step 1: Create database
    print("Step 1: Creating database...")
    if not create_database():
        return
    
    # Step 2: Create table
    print("\nStep 2: Creating table...")
    if not create_table():
        return
    
    # Step 3: Load data
    print("\nStep 3: Loading data from JSON...")
    json_file = "data.json"
    if not load_json_data(json_file):
        return
    
    # Step 4: Display sample data
    print("\nStep 4: Displaying sample data...")
    display_sample_data()
    
    print("\n=== Data loading completed successfully! ===")
    print(f"\nYou can now connect to the database using:")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {DB_USER}")
    print(f"  Table: topics")
    print(f"\nExample query:")
    print(f"  psql -U {DB_USER} -d {DB_NAME} -c 'SELECT * FROM topics LIMIT 5;'")

if __name__ == "__main__":
    main()

