"""
Authentication Routes

API endpoints for user authentication, signup, and login.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from ...services.auth_service import auth_service
from ...models.auth_models import (
    UserSignupRequest, 
    UserLoginRequest, 
    ChangePasswordRequest,
    SignupResponse, 
    LoginResponse,
    ChangePasswordResponse
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Create a new user account with validation"
)
async def signup_user(user_data: UserSignupRequest):
    """
    Create a new user account
    
    Args:
        user_data: User signup information
        
    Returns:
        SignupResponse with created user data
        
    Raises:
        HTTPException: If signup fails or user already exists
    """
    try:
        # Check if table exists
        if not auth_service.check_table_exists():
            logger.error("Users table does not exist")
            raise HTTPException(
                status_code=503, 
                detail="Database table 'users' does not exist. Please run database migration."
            )
        
        # Create user account
        user = auth_service.signup_user(user_data)
        
        logger.info(f"User signup successful for email: {user_data.email}")
        
        return SignupResponse(
            status="success",
            message="User account created successfully",
            data={
                "user": user,
                "message": "Welcome! Your account has been created successfully."
            }
        )
        
    except ValueError as e:
        logger.warning(f"Signup validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user signup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create user account. Please try again."
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login",
    description="Authenticate user and return user data"
)
async def login_user(login_data: UserLoginRequest):
    """
    Authenticate user login
    
    Args:
        login_data: User login credentials
        
    Returns:
        LoginResponse with user data and authentication info
        
    Raises:
        HTTPException: If login fails or credentials are invalid
    """
    try:
        # Check if table exists
        if not auth_service.check_table_exists():
            logger.error("Users table does not exist")
            raise HTTPException(
                status_code=503, 
                detail="Database table 'users' does not exist. Please run database migration."
            )
        
        # Authenticate user
        user = auth_service.login_user(login_data)
        
        logger.info(f"User login successful for email: {login_data.email}")
        
        return LoginResponse(
            status="success",
            message="Login successful",
            data={
                "user": user,
                "message": "Welcome back! You have been logged in successfully."
            }
        )
        
    except ValueError as e:
        logger.warning(f"Login validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Login failed. Please try again."
        )


@router.get(
    "/user/{user_id}",
    summary="Get User Profile",
    description="Get user profile by ID"
)
async def get_user_profile(user_id: int):
    """
    Get user profile by ID
    
    Args:
        user_id: User's ID
        
    Returns:
        User profile data
        
    Raises:
        HTTPException: If user not found
    """
    try:
        if user_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID"
            )
        
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        logger.info(f"User profile retrieved for ID: {user_id}")
        
        return {
            "status": "success",
            "message": "User profile retrieved successfully",
            "data": {
                "user": user
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user profile"
        )


@router.put(
    "/change-password/{user_id}",
    response_model=ChangePasswordResponse,
    summary="Change User Password",
    description="Change user password with current password verification"
)
async def change_password(user_id: int, password_data: ChangePasswordRequest):
    """
    Change user password
    
    Args:
        user_id: User's ID
        password_data: Change password request data
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If validation fails or user not found
    """
    try:
        result = auth_service.change_password(user_id, password_data)
        
        logger.info(f"Password changed successfully for user ID: {user_id}")
        
        return ChangePasswordResponse(
            status="success",
            message=result["message"],
            timestamp=datetime.now().isoformat()
        )
        
    except ValueError as e:
        logger.warning(f"Password change validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to change password"
        )
