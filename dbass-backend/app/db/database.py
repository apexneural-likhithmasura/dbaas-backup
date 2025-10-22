"""
Database Connection Manager

Handles PostgreSQL database connections with context managers for safe resource management.
"""

import logging
from contextlib import contextmanager
from typing import Generator
import psycopg2
from psycopg2.extras import RealDictCursor
from ..core.config import settings


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager with context managers"""
    
    def __init__(self):
        """Initialize database manager with connection parameters"""
        self.connection_params = {
            'host': settings.db_host,
            'port': settings.db_port,
            'database': settings.db_name,
            'user': settings.db_user,
            'password': settings.db_password
        }
        logger.info("DatabaseManager initialized")
    
    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """
        Context manager for database connections
        
        Yields:
            Database connection
            
        Example:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            logger.debug("Database connection established")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {str(e)}")
            raise e
        finally:
            if conn:
                conn.close()
                logger.debug("Database connection closed")
    
    @contextmanager
    def get_cursor(self) -> Generator[psycopg2.extensions.cursor, None, None]:
        """
        Context manager for database cursors with dict-like results
        
        Yields:
            Database cursor with RealDictCursor factory
            
        Example:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                results = cursor.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                conn.commit()
                logger.debug("Transaction committed")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back: {str(e)}")
                raise e
            finally:
                cursor.close()


# Global database manager instance
db_manager = DatabaseManager()

