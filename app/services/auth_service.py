"""
Authentication Service

Business logic for user authentication, signup, and login.
"""

import logging
import hashlib
import secrets
from contextlib import contextmanager
from typing import Optional, Dict, Any
from datetime import datetime
from ..db.database import db_manager
from ..models.auth_models import User, UserSignupRequest, UserLoginRequest, ChangePasswordRequest
from ..core.config import settings


logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service class for authentication business logic"""
    
    def __init__(self):
        """Initialize the authentication service"""
        self.table_name = "trending_data.users"
        logger.info(f"AuthenticationService initialized with table: {self.table_name}")
    
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
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256 with salt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password with salt
        """
        # Generate a random salt
        salt = secrets.token_hex(16)
        
        # Hash the password with salt
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Return salt and hash combined
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed_password: Stored hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # Split salt and hash
            salt, stored_hash = hashed_password.split(':')
            
            # Hash the provided password with the same salt
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            # Compare hashes
            return password_hash == stored_hash
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    def _user_exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email
        
        Args:
            email: User's email address
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            query = f"""
                SELECT COUNT(*) as count 
                FROM {self.table_name} 
                WHERE email = %s
            """
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (email.lower(),))
                result = cursor.fetchone()
                count = result['count'] if result else 0
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking user existence by email: {str(e)}")
            return False
    
    def _user_exists_by_username(self, username: str) -> bool:
        """
        Check if user exists by username
        
        Args:
            username: User's username
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            query = f"""
                SELECT COUNT(*) as count 
                FROM {self.table_name} 
                WHERE username = %s
            """
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (username.lower(),))
                result = cursor.fetchone()
                count = result['count'] if result else 0
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking user existence by username: {str(e)}")
            return False
    
    def signup_user(self, user_data: UserSignupRequest) -> Dict[str, Any]:
        """
        Create a new user account
        
        Args:
            user_data: User signup data
            
        Returns:
            Dictionary with created user data
            
        Raises:
            ValueError: If user already exists or validation fails
        """
        try:
            # Check if user already exists
            if self._user_exists_by_email(user_data.email):
                raise ValueError("User with this email already exists")
            
            # Auto-generate username if not provided
            username = user_data.username
            if not username:
                # Generate username from email (part before @)
                email_part = user_data.email.split('@')[0]
                username = email_part.lower()
                
                # Add random number if username already exists
                counter = 1
                original_username = username
                while self._user_exists_by_username(username):
                    username = f"{original_username}{counter}"
                    counter += 1
            else:
                if self._user_exists_by_username(username):
                    raise ValueError("Username is already taken")
            
            # Hash the password
            hashed_password = self._hash_password(user_data.password)
            
            # Prepare user data for insertion
            insert_data = {
                'first_name': user_data.first_name,
                'last_name': user_data.last_name or '',
                'email': user_data.email.lower(),
                'username': username.lower(),
                'password_hash': hashed_password,
                'phone_number': user_data.phone_number,
                'date_of_birth': user_data.date_of_birth,
                'gender': user_data.gender,
                'country': user_data.country,
                'receive_newsletters': user_data.receive_newsletters,
                'is_active': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Insert user into database
            query = f"""
                INSERT INTO {self.table_name} (
                    first_name, last_name, email, username, password_hash,
                    phone_number, date_of_birth, gender, country,
                    receive_newsletters, is_active, created_at, updated_at
                ) VALUES (
                    %(first_name)s, %(last_name)s, %(email)s, %(username)s, %(password_hash)s,
                    %(phone_number)s, %(date_of_birth)s, %(gender)s, %(country)s,
                    %(receive_newsletters)s, %(is_active)s, %(created_at)s, %(updated_at)s
                ) RETURNING id
            """
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, insert_data)
                result = cursor.fetchone()
                user_id = result['id']
                
                logger.info(f"User created successfully with ID: {user_id}")
                
                # Return user data without password
                return {
                    "id": user_id,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "email": user_data.email,
                    "username": username,  # Use the generated/validated username
                    "phone_number": user_data.phone_number,
                    "date_of_birth": user_data.date_of_birth,
                    "gender": user_data.gender,
                    "country": user_data.country,
                    "receive_newsletters": user_data.receive_newsletters,
                    "is_active": True,
                    "created_at": insert_data['created_at'].isoformat()
                }
                
        except ValueError as e:
            logger.warning(f"Signup validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def login_user(self, login_data: UserLoginRequest) -> Dict[str, Any]:
        """
        Authenticate user login
        
        Args:
            login_data: User login credentials
            
        Returns:
            Dictionary with user data and authentication info
            
        Raises:
            ValueError: If credentials are invalid
        """
        try:
            # Get user by email
            query = f"""
                SELECT id, first_name, last_name, email, username, password_hash,
                       phone_number, date_of_birth, gender, country,
                       receive_newsletters, is_active, created_at, updated_at
                FROM {self.table_name}
                WHERE email = %s AND is_active = true
            """
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (login_data.email.lower(),))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError("Invalid email or password")
                
                # Verify password
                if not self._verify_password(login_data.password, result['password_hash']):
                    raise ValueError("Invalid email or password")
                
                # Update last login time
                update_query = f"""
                    UPDATE {self.table_name}
                    SET updated_at = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (datetime.now(), result['id']))
                
                logger.info(f"User {result['email']} logged in successfully")
                
                # Return user data without password
                return {
                    "id": result['id'],
                    "first_name": result['first_name'],
                    "last_name": result['last_name'],
                    "email": result['email'],
                    "username": result['username'],
                    "phone_number": result['phone_number'],
                    "date_of_birth": result['date_of_birth'],
                    "gender": result['gender'],
                    "country": result['country'],
                    "receive_newsletters": result['receive_newsletters'],
                    "is_active": result['is_active'],
                    "created_at": result['created_at'].isoformat() if result['created_at'] else None,
                    "updated_at": result['updated_at'].isoformat() if result['updated_at'] else None,
                    "last_login": datetime.now().isoformat()
                }
                
        except ValueError as e:
            logger.warning(f"Login validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User's ID
            
        Returns:
            User data dictionary or None if not found
        """
        try:
            query = f"""
                SELECT id, first_name, last_name, email, username,
                       phone_number, date_of_birth, gender, country,
                       receive_newsletters, is_active, created_at, updated_at
                FROM {self.table_name}
                WHERE id = %s AND is_active = true
            """
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "id": result['id'],
                        "first_name": result['first_name'],
                        "last_name": result['last_name'],
                        "email": result['email'],
                        "username": result['username'],
                        "phone_number": result['phone_number'],
                        "date_of_birth": result['date_of_birth'],
                        "gender": result['gender'],
                        "country": result['country'],
                        "receive_newsletters": result['receive_newsletters'],
                        "is_active": result['is_active'],
                        "created_at": result['created_at'].isoformat() if result['created_at'] else None,
                        "updated_at": result['updated_at'].isoformat() if result['updated_at'] else None
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    def change_password(self, user_id: int, password_data: ChangePasswordRequest) -> Dict[str, Any]:
        """
        Change user password
        
        Args:
            user_id: User's ID
            password_data: Change password request data
            
        Returns:
            Success message dictionary
            
        Raises:
            ValueError: If current password is incorrect or user not found
        """
        try:
            # First verify the current password
            query = f"""
                SELECT id, password_hash
                FROM {self.table_name}
                WHERE id = %s AND is_active = true
            """
            
            with self._get_db_cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError("User not found or inactive")
                
                # Verify current password
                stored_hash = result['password_hash']
                if not self._verify_password(password_data.current_password, stored_hash):
                    raise ValueError("Current password is incorrect")
                
                # Hash the new password
                new_password_hash = self._hash_password(password_data.new_password)
                
                # Update the password
                update_query = f"""
                    UPDATE {self.table_name}
                    SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                
                cursor.execute(update_query, (new_password_hash, user_id))
                
                logger.info(f"Password changed successfully for user ID: {user_id}")
                
                return {
                    "message": "Password changed successfully"
                }
                
        except ValueError as e:
            logger.warning(f"Password change validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
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
        Check if the users table exists
        
        Returns:
            True if table exists, False otherwise
        """
        try:
            with self._get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = %s 
                        AND table_name = 'users'
                    )
                """, (settings.db_schema,))
                result = cursor.fetchone()
                exists = result['exists'] if result else False
                logger.info(f"Users table exists check: {exists}")
                return exists
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False


# Global service instance
auth_service = AuthenticationService()
