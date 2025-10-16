#!/usr/bin/env python3
"""
FastAPI application for Topics Database
Provides endpoints to retrieve and filter topics data from PostgreSQL
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Database configuration
import os

# Get database connection parameters from environment or use defaults
DB_NAME = os.getenv("DB_NAME", "topics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword123")  # Default password provided
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Build connection string
if DB_PASSWORD:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize FastAPI app
app = FastAPI(
    title="Topics API",
    description="API to retrieve trending topics data with filtering capabilities",
    version="1.0.0"
)

# Pydantic models for response
class Topic(BaseModel):
    """Topic data model"""
    id: int
    topic: str
    volume: Optional[str] = None
    growth: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    time_period: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TopicsResponse(BaseModel):
    """Response model for topics list"""
    total: int
    time_period_filter: Optional[str] = None
    data: List[Topic]


# Database connection context manager
@contextmanager
def get_db_connection():
    """Get database connection with context manager"""
    conn = None
    try:
        # Try multiple connection methods in order of preference
        
        # Method 1: If password is provided, use it
        if DB_PASSWORD:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
        else:
            # Method 2: Try peer authentication (Unix socket)
            try:
                conn = psycopg2.connect(dbname=DB_NAME)
            except psycopg2.OperationalError:
                # Method 3: Try without password (trust authentication)
                try:
                    conn = psycopg2.connect(
                        dbname=DB_NAME,
                        user=DB_USER,
                        host=DB_HOST,
                        port=DB_PORT
                    )
                except psycopg2.OperationalError:
                    # Method 4: Try with empty password (if md5 auth is configured)
                    try:
                        conn = psycopg2.connect(
                            dbname=DB_NAME,
                            user=DB_USER,
                            password="",
                            host=DB_HOST,
                            port=DB_PORT
                        )
                    except psycopg2.OperationalError as e:
                        # All methods failed, provide helpful error
                        error_msg = str(e)
                        if "fe_sendauth: no password supplied" in error_msg:
                            raise HTTPException(
                                status_code=500,
                                detail="Database connection error: PostgreSQL requires password authentication. Please run the API as postgres user: sudo -u postgres python3 pgmain.py OR set DB_PASSWORD environment variable."
                            )
                        elif "role" in error_msg and "does not exist" in error_msg:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Database connection error: {error_msg}. Please run the API as 'postgres' user: sudo -u postgres python3 pgmain.py"
                            )
                        else:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Database connection error: {error_msg}"
                            )
        yield conn
    except HTTPException:
        raise
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Topics API",
        "version": "1.0.0",
        "endpoints": {
            "/topics": "Get all topics with optional filtering",
            "/topics/stats": "Get statistics about topics",
            "/docs": "API documentation"
        }
    }


def normalize_time_period(time_period: str) -> str:
    """
    Normalize time period input to match database format.
    Accepts: '2', '10', '15' or '2 Years', '10 Years', '15 Years'
    Returns: '2 Years', '10 Years', or '15 Years'
    """
    if not time_period:
        return None
    
    # If already in correct format, return as is
    if 'year' in time_period.lower():
        return time_period
    
    # If just a number, add 'Years'
    time_period = time_period.strip()
    if time_period.isdigit():
        return f"{time_period} Years"
    
    return time_period


@app.get("/topics", response_model=TopicsResponse, tags=["Topics"])
async def get_topics(
    time_period: Optional[str] = Query(
        None,
        description="Filter topics by time period. Accepts: '2', '10', '15' or '2 Years', '10 Years', '15 Years'",
        examples=["2 Years", "10 Years", "15 Years", "2", "10", "15"]
    ),
    limit: Optional[int] = Query(
        None,
        description="Limit the number of results",
        ge=1,
        le=1000
    ),
    offset: Optional[int] = Query(
        0,
        description="Number of records to skip",
        ge=0
    ),
    search: Optional[str] = Query(
        None,
        description="Search topics by keyword",
        min_length=1
    )
):
    """
    Get topics from the database with optional filtering.
    
    Parameters:
    - **time_period**: Filter by time period. Accepts '2', '10', '15' or '2 Years', '10 Years', '15 Years'
    - **limit**: Maximum number of results to return
    - **offset**: Number of records to skip (for pagination)
    - **search**: Search keyword in topic name or description
    
    Returns:
    - List of topics matching the filters
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Build query
            query = "SELECT * FROM topics WHERE 1=1"
            params = []
            
            # Add time_period filter with normalization
            if time_period:
                normalized_period = normalize_time_period(time_period)
                query += " AND time_period = %s"
                params.append(normalized_period)
            
            # Add search filter
            if search:
                query += " AND (topic ILIKE %s OR description ILIKE %s)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern])
            
            # Add ordering
            query += " ORDER BY id"
            
            # Add pagination
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            if offset:
                query += " OFFSET %s"
                params.append(offset)
            
            # Execute query
            cursor.execute(query, params)
            topics = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) as count FROM topics WHERE 1=1"
            count_params = []
            
            if time_period:
                normalized_period = normalize_time_period(time_period)
                count_query += " AND time_period = %s"
                count_params.append(normalized_period)
            
            if search:
                count_query += " AND (topic ILIKE %s OR description ILIKE %s)"
                search_pattern = f"%{search}%"
                count_params.extend([search_pattern, search_pattern])
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()['count']
            
            cursor.close()
            
            return TopicsResponse(
                total=total,
                time_period_filter=time_period,
                data=topics
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving topics: {str(e)}"
        )


@app.get("/topics/stats", tags=["Topics"])
async def get_topics_stats():
    """
    Get statistics about topics in the database.
    
    Returns:
    - Total count of topics
    - Breakdown by time period
    - Top growth topics
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Total count
            cursor.execute("SELECT COUNT(*) as total FROM topics")
            total = cursor.fetchone()['total']
            
            # Count by time period
            cursor.execute("""
                SELECT time_period, COUNT(*) as count 
                FROM topics 
                GROUP BY time_period 
                ORDER BY time_period
            """)
            by_time_period = cursor.fetchall()
            
            # Get unique time periods
            cursor.execute("""
                SELECT DISTINCT time_period 
                FROM topics 
                ORDER BY time_period
            """)
            time_periods = [row['time_period'] for row in cursor.fetchall()]
            
            cursor.close()
            
            return {
                "total_topics": total,
                "available_time_periods": time_periods,
                "breakdown_by_time_period": by_time_period
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@app.get("/topics/top/{time_period}", tags=["Topics"])
async def get_top_topics_by_year(
    time_period: str
):
    """
    Get top 6 topics based on time period.
    
    Parameters:
    - **time_period**: Time period to filter. Accepts '2', '10', '15' or '2 Years', '10 Years', '15 Years'
    
    Returns:
    - Top 6 topics for the specified time period, sorted by growth percentage (highest first)
    """
    try:
        # Normalize time period
        normalized_period = normalize_time_period(time_period)
        
        if not normalized_period:
            raise HTTPException(
                status_code=400,
                detail="Invalid time period. Use '2', '10', '15' or '2 Years', '10 Years', '15 Years'"
            )
        
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Query to get top 6 topics by growth for the specified time period
            # Clean the growth string and convert to numeric for sorting
            query = """
                SELECT * FROM topics 
                WHERE time_period = %s 
                ORDER BY 
                    CAST(
                        REGEXP_REPLACE(growth, '[^0-9]', '', 'g') AS INTEGER
                    ) DESC 
                LIMIT 6
            """
            
            cursor.execute(query, (normalized_period,))
            topics = cursor.fetchall()
            
            cursor.close()
            
            if not topics:
                raise HTTPException(
                    status_code=404,
                    detail=f"No topics found for time period: {time_period}"
                )
            
            return {
                "time_period": normalized_period,
                "time_period_requested": time_period,
                "count": len(topics),
                "top_topics": topics
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving top topics: {str(e)}"
        )


@app.get("/topics/{topic_id}", response_model=Topic, tags=["Topics"])
async def get_topic_by_id(topic_id: int):
    """
    Get a specific topic by ID.
    
    Parameters:
    - **topic_id**: The ID of the topic to retrieve
    
    Returns:
    - Topic details
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM topics WHERE id = %s", (topic_id,))
            topic = cursor.fetchone()
            
            cursor.close()
            
            if not topic:
                raise HTTPException(
                    status_code=404,
                    detail=f"Topic with ID {topic_id} not found"
                )
            
            return topic
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving topic: {str(e)}"
        )


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify database connectivity.
    
    Returns:
    - Status of the API and database connection
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API is running and database is accessible"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    print("Starting Topics API server...")
    print("API Documentation will be available at: http://192.168.1.45:8001/docs")
    print("Alternative docs at: http://192.168.1.45:8001/redoc")
    uvicorn.run(app, host="192.168.1.45", port=8001, log_level="info")

