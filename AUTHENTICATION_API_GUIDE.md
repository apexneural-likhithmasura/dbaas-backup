# Authentication API Guide

## Overview

Complete authentication system with signup and login APIs, fully integrated into your existing FastAPI backend without touching any existing code.

## 🚀 API Endpoints

### Base URL: `http://localhost:8000/dbas/api/auth`

---

## 📝 1. User Signup

**Endpoint:** `POST /dbas/api/auth/signup`

Create a new user account with comprehensive validation.

### Request Body

```json
{
  "first_name": "John",
  "last_name": "Doe", 
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "country": "United States",
  "accept_terms": true,
  "accept_privacy_policy": true,
  "receive_newsletters": false,
  "username": "johndoe123"
}
```

### Field Validation

- **first_name**: Required, 1-50 characters
- **last_name**: Required, 1-50 characters  
- **email**: Required, valid email format, unique
- **username**: Required, 3-30 characters, alphanumeric + underscore only, unique
- **password**: Required, 8+ characters, must contain:
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 digit
  - At least 1 special character
- **confirm_password**: Must match password
- **phone_number**: Optional, 10-15 digits
- **date_of_birth**: Optional, YYYY-MM-DD format
- **gender**: Optional, one of: male, female, other, prefer_not_to_say
- **country**: Optional, any string
- **accept_terms**: Required, must be true
- **accept_privacy_policy**: Required, must be true
- **receive_newsletters**: Optional, boolean

### Response (201 Created)

```json
{
  "status": "success",
  "message": "User account created successfully",
  "data": {
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "username": "johndoe123",
      "phone_number": "+1234567890",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "country": "United States",
      "receive_newsletters": false,
      "is_active": true,
      "created_at": "2025-10-23T05:37:04.528543"
    },
    "message": "Welcome! Your account has been created successfully."
  },
  "timestamp": "2025-10-23T05:37:04.851652"
}
```

---

## 🔐 2. User Login

**Endpoint:** `POST /dbas/api/auth/login`

Authenticate user and return user data.

### Request Body

```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!"
}
```

### Response (200 OK)

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "username": "johndoe123",
      "phone_number": "+1234567890",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "country": "United States",
      "receive_newsletters": false,
      "is_active": true,
      "created_at": "2025-10-23T05:37:04.528543",
      "updated_at": "2025-10-23T05:37:04.528548",
      "last_login": "2025-10-23T05:37:14.676556"
    },
    "message": "Welcome back! You have been logged in successfully."
  },
  "timestamp": "2025-10-23T05:37:14.704078"
}
```

---

## 👤 3. Get User Profile

**Endpoint:** `GET /dbas/api/auth/user/{user_id}`

Retrieve user profile by ID.

### Response (200 OK)

```json
{
  "status": "success",
  "message": "User profile retrieved successfully",
  "data": {
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "username": "johndoe123",
      "phone_number": "+1234567890",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "country": "United States",
      "receive_newsletters": false,
      "is_active": true,
      "created_at": "2025-10-23T05:37:04.528543",
      "updated_at": "2025-10-23T05:37:14.156097"
    }
  }
}
```

---

## 🏥 4. Health Check

**Endpoint:** `GET /dbas/api/auth/health/check`

Check authentication service status.

### Response (200 OK)

```json
{
  "status": "success",
  "message": "Authentication service is healthy",
  "data": {
    "database_connected": true,
    "table_exists": true,
    "service_status": "healthy"
  }
}
```

---

## 🧪 Testing Examples

### cURL Commands

```bash
# 1. Signup
curl -X POST http://localhost:8000/dbas/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "country": "United States",
    "accept_terms": true,
    "accept_privacy_policy": true,
    "receive_newsletters": false,
    "username": "johndoe123"
  }'

# 2. Login
curl -X POST http://localhost:8000/dbas/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePassword123!"
  }'

# 3. Get Profile
curl http://localhost:8000/dbas/api/auth/user/1

# 4. Health Check
curl http://localhost:8000/dbas/api/auth/health/check
```

### Python Example

```python
import requests

# Signup
signup_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "country": "United States",
    "accept_terms": True,
    "accept_privacy_policy": True,
    "receive_newsletters": False,
    "username": "johndoe123"
}

response = requests.post(
    "http://localhost:8000/dbas/api/auth/signup",
    json=signup_data
)
print(response.json())

# Login
login_data = {
    "email": "john.doe@example.com",
    "password": "SecurePassword123!"
}

response = requests.post(
    "http://localhost:8000/dbas/api/auth/login",
    json=login_data
)
print(response.json())
```

### JavaScript Example

```javascript
// Signup
const signupData = {
  first_name: "John",
  last_name: "Doe",
  email: "john.doe@example.com",
  password: "SecurePassword123!",
  confirm_password: "SecurePassword123!",
  phone_number: "+1234567890",
  date_of_birth: "1990-01-15",
  gender: "male",
  country: "United States",
  accept_terms: true,
  accept_privacy_policy: true,
  receive_newsletters: false,
  username: "johndoe123"
};

fetch('http://localhost:8000/dbas/api/auth/signup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(signupData)
})
.then(response => response.json())
.then(data => console.log(data));

// Login
const loginData = {
  email: "john.doe@example.com",
  password: "SecurePassword123!"
};

fetch('http://localhost:8000/dbas/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 🗄️ Database Schema

### Users Table Structure

```sql
CREATE TABLE trending_data.users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(30) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(20),
    country VARCHAR(100),
    receive_newsletters BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Security Features

- **Password Hashing**: SHA-256 with random salt
- **Input Validation**: Comprehensive field validation
- **SQL Injection Protection**: Parameterized queries
- **Unique Constraints**: Email and username uniqueness
- **Active Status**: Account activation/deactivation

---

## 🏗️ Architecture

### File Structure

```
app/
├── models/
│   └── auth_models.py          # Pydantic models
├── services/
│   └── auth_service.py         # Business logic
├── api/routes/
│   └── auth_routes.py          # API endpoints
└── db/
    └── database.py             # Database connection (shared)

scripts/
├── create_users_table.sql      # Database schema
└── run_migration.py           # Migration script
```

### Components

1. **Models** (`auth_models.py`)
   - `UserSignupRequest`: Signup validation
   - `UserLoginRequest`: Login validation
   - `User`: Complete user model
   - `AuthResponse`: Standardized responses

2. **Service** (`auth_service.py`)
   - Password hashing/verification
   - User creation and authentication
   - Database operations
   - Input validation

3. **Routes** (`auth_routes.py`)
   - RESTful API endpoints
   - Error handling
   - Response formatting

---

## ⚠️ Error Handling

### Common Error Responses

#### 400 Bad Request (Validation Error)
```json
{
  "detail": "Username can only contain letters, numbers, and underscores"
}
```

#### 401 Unauthorized (Login Failed)
```json
{
  "detail": "Invalid email or password"
}
```

#### 409 Conflict (User Exists)
```json
{
  "detail": "User with this email already exists"
}
```

#### 503 Service Unavailable (Database Issue)
```json
{
  "detail": "Database table 'users' does not exist. Please run database migration."
}
```

---

## 🚀 Setup Instructions

### 1. Database Migration

```bash
# Run the migration script
source ~/dbass/bin/activate
cd /root/dbas/backend-final/dbass-backend
python scripts/run_migration.py
```

### 2. Start Server

```bash
# Start the server
python run.py
```

### 3. Test Endpoints

```bash
# Health check
curl http://localhost:8000/dbas/api/auth/health/check

# View API docs
open http://localhost:8000/dbas/api/docs
```

---

## 📊 Current Status

✅ **Database**: Connected to `dbass_production`  
✅ **Table**: `trending_data.users` created  
✅ **Endpoints**: All 4 endpoints working  
✅ **Validation**: Comprehensive input validation  
✅ **Security**: Password hashing implemented  
✅ **Testing**: All endpoints tested successfully  

---

## 🔗 Integration

The authentication system is fully integrated with your existing API:

- **Base URL**: `/dbas/api/auth`
- **Documentation**: Available at `/dbas/api/docs`
- **No Conflicts**: Zero impact on existing endpoints
- **Shared Database**: Uses same connection as trending topics

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/dbas/api/docs
- **ReDoc**: http://localhost:8000/dbas/api/redoc
- **Migration Script**: `scripts/run_migration.py`
- **Database Schema**: `scripts/create_users_table.sql`

---

**Authentication system is fully operational!** 🎉
