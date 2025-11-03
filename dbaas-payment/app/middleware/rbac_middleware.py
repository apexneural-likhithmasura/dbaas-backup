"""
Rate Limiting Middleware

Rate limiting middleware for API endpoints.
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Rate limiting middleware for API endpoints"""
    
    def __init__(self, requests_per_minute: int = 100):
        """Initialize rate limiting middleware"""
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # In production, use Redis or similar
        logger.info(f"Rate limiting initialized: {requests_per_minute} requests/minute")
    
    async def check_rate_limit(self, request: Request, admin_id: Optional[int] = None) -> bool:
        """Check if request is within rate limit"""
        try:
            # Get client IP as fallback if admin_id not available
            client_id = str(admin_id) if admin_id else request.client.host
            
            current_time = int(datetime.now().timestamp())
            minute_window = current_time // 60
            
            # Clean old entries
            self._cleanup_old_entries(minute_window)
            
            # Check current rate
            key = f"{client_id}:{minute_window}"
            current_requests = self.requests.get(key, 0)
            
            if current_requests >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for {client_id}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
                )
            
            # Increment counter
            self.requests[key] = current_requests + 1
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # Allow request on error to avoid blocking legitimate users
            return True
    
    def _cleanup_old_entries(self, current_minute: int):
        """Clean up old rate limit entries"""
        keys_to_remove = []
        for key in self.requests:
            try:
                _, minute = key.split(':')
                if int(minute) < current_minute - 1:  # Keep current and previous minute
                    keys_to_remove.append(key)
            except ValueError:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]


# Global middleware instance
rate_limit_middleware = RateLimitMiddleware()
