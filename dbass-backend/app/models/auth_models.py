"""
Authentication Models

Pydantic models for user authentication, signup, and login.
"""

import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr


class UserBase(BaseModel):
    """Base user model with common fields"""
    
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="User's first name"
    )
    
    last_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="User's last name"
    )
    
    email: EmailStr = Field(
        ..., 
        description="User's email address"
    )
    
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Unique username"
    )
    
    phone_number: Optional[str] = Field(
        None, 
        description="User's phone number"
    )
    
    date_of_birth: Optional[str] = Field(
        None, 
        description="User's date of birth (YYYY-MM-DD)"
    )
    
    gender: Optional[str] = Field(
        None, 
        description="User's gender"
    )
    
    country: Optional[str] = Field(
        None, 
        description="User's country"
    )
    
    receive_newsletters: bool = Field(
        default=False, 
        description="Whether user wants to receive newsletters"
    )
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format or auto-generate if not provided"""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Username can only contain letters, numbers, and underscores')
            return v.lower()
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        if v is not None:
            # Remove all non-digit characters
            digits = re.sub(r'\D', '', v)
            if len(digits) < 10 or len(digits) > 15:
                raise ValueError('Phone number must be between 10-15 digits')
        return v
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth format"""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Date of birth must be in YYYY-MM-DD format')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        """Validate gender values"""
        if v is not None:
            allowed_genders = ['male', 'female', 'other', 'prefer_not_to_say']
            if v.lower() not in allowed_genders:
                raise ValueError(f'Gender must be one of: {", ".join(allowed_genders)}')
        return v


class UserSignupRequest(BaseModel):
    """User signup request model - all fields available, only 4 mandatory"""
    
    # MANDATORY FIELDS (4 only)
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="User's first name (REQUIRED)"
    )
    
    email: EmailStr = Field(
        ..., 
        description="User's email address (REQUIRED)"
    )
    
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="User's password (REQUIRED)"
    )
    
    confirm_password: str = Field(
        ..., 
        description="Password confirmation (REQUIRED)"
    )
    
    # OPTIONAL FIELDS (all available but not mandatory)
    last_name: Optional[str] = Field(
        None, 
        max_length=50, 
        description="User's last name (optional)"
    )
    
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=30, 
        description="Unique username (optional - auto-generated if not provided)"
    )
    
    phone_number: Optional[str] = Field(
        None, 
        description="User's phone number (optional)"
    )
    
    date_of_birth: Optional[str] = Field(
        None, 
        description="User's date of birth - YYYY-MM-DD format (optional)"
    )
    
    gender: Optional[str] = Field(
        None, 
        description="User's gender - male/female/other/prefer_not_to_say (optional)"
    )
    
    country: Optional[str] = Field(
        None, 
        description="User's country (optional)"
    )
    
    receive_newsletters: bool = Field(
        default=False, 
        description="Whether user wants to receive newsletters (optional, default: false)"
    )
    
    accept_terms: bool = Field(
        default=True, 
        description="Terms and conditions acceptance (optional, default: true)"
    )
    
    accept_privacy_policy: bool = Field(
        default=True, 
        description="Privacy policy acceptance (optional, default: true)"
    )
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """Validate password confirmation"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('accept_terms')
    def validate_accept_terms(cls, v):
        """Validate terms acceptance (optional with default True)"""
        return v
    
    @validator('accept_privacy_policy')
    def validate_accept_privacy_policy(cls, v):
        """Validate privacy policy acceptance (optional with default True)"""
        return v


class UserLoginRequest(BaseModel):
    """User login request model"""
    
    email: EmailStr = Field(
        ..., 
        description="User's email address"
    )
    
    password: str = Field(
        ..., 
        min_length=1, 
        description="User's password"
    )


class ChangePasswordRequest(BaseModel):
    """Change password request model"""
    
    current_password: str = Field(
        ...,
        min_length=1,
        description="Current password"
    )
    
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password"
    )
    
    confirm_new_password: str = Field(
        ...,
        description="Confirm new password"
    )
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('confirm_new_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v


class User(BaseModel):
    """Complete user model with ID and timestamps"""
    
    id: int = Field(
        ..., 
        gt=0, 
        description="Unique user identifier"
    )
    
    first_name: str = Field(
        ..., 
        description="User's first name"
    )
    
    last_name: str = Field(
        ..., 
        description="User's last name"
    )
    
    email: str = Field(
        ..., 
        description="User's email address"
    )
    
    username: str = Field(
        ..., 
        description="User's username"
    )
    
    phone_number: Optional[str] = Field(
        None, 
        description="User's phone number"
    )
    
    date_of_birth: Optional[str] = Field(
        None, 
        description="User's date of birth"
    )
    
    gender: Optional[str] = Field(
        None, 
        description="User's gender"
    )
    
    country: Optional[str] = Field(
        None, 
        description="User's country"
    )
    
    receive_newsletters: bool = Field(
        default=False, 
        description="Newsletter subscription status"
    )
    
    is_active: bool = Field(
        default=True, 
        description="Whether user account is active"
    )
    
    created_at: datetime = Field(
        ..., 
        description="Account creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        None, 
        description="Last update timestamp"
    )
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AuthResponse(BaseModel):
    """Authentication response model"""
    
    status: str = Field(
        ..., 
        description="Response status (success/error)"
    )
    
    message: str = Field(
        ..., 
        description="Response message"
    )
    
    data: Optional[dict] = Field(
        None, 
        description="Response data"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now, 
        description="Response timestamp"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class LoginResponse(AuthResponse):
    """Login response model with user data"""
    
    data: dict = Field(
        ..., 
        description="User data and authentication info"
    )


class SignupResponse(AuthResponse):
    """Signup response model with user data"""
    
    data: dict = Field(
        ..., 
        description="Created user data"
    )


class ChangePasswordResponse(AuthResponse):
    """Change password response model"""
    
    pass  # Inherits status, message, and timestamp from AuthResponse
