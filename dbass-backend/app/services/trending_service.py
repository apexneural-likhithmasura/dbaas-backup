"""
Trending Topics Service

Business logic for trending topics operations.
"""

import logging
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from ..db.database import db_manager
from ..models.trending_models import TrendingTopic
from ..core.config import settings


logger = logging.getLogger(__name__)


class TrendingTopicsService:
    """Service class for trending topics business logic"""
    
    def __init__(self):
        """Initialize the trending topics service"""
        self.table_name = f"{settings.db_schema}.trending_topics"
        logger.info(f"TrendingTopicsService initialized with table: {self.table_name}")
    
    @contextmanager
    def _get_db_cursor(self):
        """
        Context manager for database operations with proper error handling
        
        Yields:
            Database cursor
        """
        try:
            with db_manager.get_cursor() as cursor:
                yield cursor
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise
    
    def get_all_topics(self, limit: Optional[int] = None, offset: int = 0) -> List[TrendingTopic]:
        """
        Get all trending topics with optional pagination
        
        Args:
            limit: Maximum number of topics to return
            offset: Number of topics to skip
            
        Returns:
            List of TrendingTopic objects
        """
        try:
            query = f"""
                SELECT id, topic, volume, growth, description, url, time_period, created_at
                FROM {self.table_name}
                ORDER BY id
            """
            
            params = []
            if limit:
                query += " LIMIT %s OFFSET %s"
                params = [limit, offset]
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                topics = [TrendingTopic(**dict(row)) for row in results]
                logger.info(f"Retrieved {len(topics)} topics")
                return topics
                
        except Exception as e:
            logger.error(f"Error getting all topics: {str(e)}")
            raise
    
    def get_topic_by_id(self, topic_id: int) -> Optional[TrendingTopic]:
        """
        Get a specific topic by ID
        
        Args:
            topic_id: The ID of the topic to retrieve
            
        Returns:
            TrendingTopic object or None if not found
        """
        try:
            if topic_id <= 0:
                raise ValueError("Topic ID must be positive")
                
            query = f"""
                SELECT id, topic, volume, growth, description, url, time_period, created_at
                FROM {self.table_name}
                WHERE id = %s
            """
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (topic_id,))
                result = cursor.fetchone()
                
                if result:
                    topic = TrendingTopic(**dict(result))
                    logger.info(f"Retrieved topic with ID: {topic_id}")
                    return topic
                else:
                    logger.warning(f"Topic not found with ID: {topic_id}")
                    return None
                    
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting topic by ID {topic_id}: {str(e)}")
            raise
    
    def get_top_growth_topics(self, limit: int = 6) -> List[TrendingTopic]:
        """
        Get topics with highest growth percentage
        
        Args:
            limit: Maximum number of topics to return (default: 6)
            
        Returns:
            List of TrendingTopic objects sorted by growth percentage
        """
        query = f"""
            SELECT id, topic, volume, growth, description, url, time_period, created_at
            FROM {self.table_name}
        """
        
        try:
            with self._get_db_cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                if not results:
                    logger.warning("No topics found in database")
                    return []
                
                # Convert to TrendingTopic objects
                topics = [TrendingTopic(**dict(row)) for row in results]
                logger.info(f"Retrieved {len(topics)} topics from database")
                
                # Filter and sort by growth percentage in Python
                topic_dict = {}  # To track unique topics
                
                for topic in topics:
                    if topic.growth.startswith('+') and topic.growth.endswith('%'):
                        try:
                            # Extract numeric value from growth string
                            growth_value = int(topic.growth.replace('+', '').replace('%', ''))
                            
                            # Keep only the highest growth version of each topic
                            if topic.topic not in topic_dict or growth_value > topic_dict[topic.topic][1]:
                                topic_dict[topic.topic] = (topic, growth_value)
                        except ValueError as ve:
                            logger.warning(f"Failed to parse growth value '{topic.growth}': {ve}")
                            continue
                
                logger.info(f"Found {len(topic_dict)} unique topics with valid growth")
                
                # Convert to list and sort by growth value descending
                growth_topics = list(topic_dict.values())
                growth_topics.sort(key=lambda x: x[1], reverse=True)
                final_topics = [topic for topic, _ in growth_topics[:limit]]
                
                logger.info(f"Returning {len(final_topics)} top growth topics")
                return final_topics
                
        except Exception as e:
            logger.error(f"Error getting top growth topics: {str(e)}")
            return []
    
    def search_topics(self, search_term: str, limit: Optional[int] = None) -> List[TrendingTopic]:
        """
        Search topics by name or description
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching TrendingTopic objects
        """
        query = f"""
            SELECT id, topic, volume, growth, description, url, time_period, created_at
            FROM {self.table_name}
            WHERE topic ILIKE %s OR description ILIKE %s
            ORDER BY 
                CASE 
                    WHEN topic ILIKE %s THEN 1 
                    ELSE 2 
                END,
                id
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        search_pattern = f"%{search_term}%"
        topic_pattern = f"%{search_term}%"
        
        try:
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (search_pattern, search_pattern, topic_pattern))
                results = cursor.fetchall()
                topics = [TrendingTopic(**dict(row)) for row in results]
                logger.info(f"Search for '{search_term}' returned {len(topics)} results")
                return topics
        except Exception as e:
            logger.error(f"Error searching topics: {str(e)}")
            raise
    
    def get_topics_by_time_period(self, time_period: str) -> List[TrendingTopic]:
        """
        Get topics filtered by time period
        
        Args:
            time_period: Time period to filter by
            
        Returns:
            List of TrendingTopic objects
        """
        query = f"""
            SELECT id, topic, volume, growth, description, url, time_period, created_at
            FROM {self.table_name}
            WHERE time_period = %s
            ORDER BY id
        """
        
        try:
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (time_period,))
                results = cursor.fetchall()
                topics = [TrendingTopic(**dict(row)) for row in results]
                logger.info(f"Retrieved {len(topics)} topics for time period: {time_period}")
                return topics
        except Exception as e:
            logger.error(f"Error getting topics by time period: {str(e)}")
            raise
    
    def get_total_count(self) -> int:
        """
        Get total number of topics
        
        Returns:
            Total count of topics in database
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                count = result['count'] if result and 'count' in result else 0
                logger.info(f"Total topics count: {count}")
                return count
                
        except Exception as e:
            logger.error(f"Error getting total count: {str(e)}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get various statistics about the trending topics
        
        Returns:
            Dictionary containing statistics
        """
        stats_query = f"""
            SELECT 
                COUNT(*) as total_topics,
                COUNT(DISTINCT time_period) as unique_time_periods,
                AVG(CAST(REPLACE(REPLACE(growth, '+', ''), '%', '') AS INTEGER)) as avg_growth
            FROM {self.table_name}
            WHERE growth ~ '^\\+[0-9]+%$'
        """
        
        time_periods_query = f"""
            SELECT time_period, COUNT(*) as count
            FROM {self.table_name}
            GROUP BY time_period
            ORDER BY count DESC
        """
        
        try:
            with self._get_db_cursor() as cursor:
                # Get general statistics
                cursor.execute(stats_query)
                stats = dict(cursor.fetchone())
                
                # Get time period breakdown
                cursor.execute(time_periods_query)
                time_periods = [dict(row) for row in cursor.fetchall()]
                
                result = {
                    "total_topics": stats["total_topics"],
                    "unique_time_periods": stats["unique_time_periods"],
                    "average_growth": round(float(stats["avg_growth"]) if stats["avg_growth"] else 0, 2),
                    "time_period_breakdown": time_periods
                }
                logger.info("Statistics retrieved successfully")
                return result
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise
    
    def check_database_connection(self) -> bool:
        """
        Check if database connection is working
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self._get_db_cursor() as cursor:
                cursor.execute("SELECT 1")
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    def check_table_exists(self) -> bool:
        """
        Check if the trending_topics table exists
        
        Returns:
            True if table exists, False otherwise
        """
        try:
            with self._get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = %s 
                        AND table_name = 'trending_topics'
                    )
                """, (settings.db_schema,))
                result = cursor.fetchone()
                exists = result['exists'] if result else False
                logger.info(f"Table exists check: {exists}")
                return exists
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False


# Global service instance
trending_service = TrendingTopicsService()

