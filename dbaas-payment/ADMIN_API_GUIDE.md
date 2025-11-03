# Admin & Settings API Guide

## Overview

Production-level admin and settings management system for the DBAAS backend. This system provides comprehensive user management, role-based access control, and system configuration management.

## 🚀 Base URLs

- **Admin API**: `http://localhost:8000/dbas/api/admin`
- **Settings API**: `http://localhost:8000/dbas/api/settings`
- **API Documentation**: `http://localhost:8000/dbas/api/docs`

---

## 🔐 Admin Management API

### User Management

#### 1. Get All Users
```http
GET /dbas/api/admin/users?page=1&limit=50&status=active
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50, max: 100)
- `status` (optional): Filter by status (`active`, `inactive`, `banned`, `suspended`)

**Response:**
```json
{
  "status": "success",
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "phone_number": "+1234567890",
        "date_of_birth": "1990-01-15",
        "gender": "male",
        "country": "United States",
        "receive_newsletters": true,
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 100,
      "pages": 2
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 2. Get User by ID
```http
GET /dbas/api/admin/users/{user_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "username": "johndoe",
      "phone_number": "+1234567890",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "country": "United States",
      "receive_newsletters": true,
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 3. Update User Status
```http
PUT /dbas/api/admin/users/{user_id}/status
```

**Request Body:**
```json
{
  "user_id": 1,
  "action": "ban",
  "reason": "Violation of terms of service"
}
```

**Actions:**
- `ban`: Ban the user
- `unban`: Unban the user
- `suspend`: Suspend the user
- `activate`: Activate the user

**Response:**
```json
{
  "status": "success",
  "message": "User banned successfully",
  "data": {
    "message": "User banned successfully",
    "user_id": 1,
    "status": "ban",
    "reason": "Violation of terms of service"
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 4. Delete User
```http
DELETE /dbas/api/admin/users/{user_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "User deleted successfully",
  "data": {
    "message": "User deleted successfully",
    "user_id": 1
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Admin User Management

#### 5. Create Admin User
```http
POST /dbas/api/admin/admin-users
```

**Request Body:**
```json
{
  "user_id": 1,
  "role": "admin",
  "permissions": ["create_user", "read_user", "update_user"]
}
```

**Roles:**
- `super_admin`: Full access to all features
- `admin`: Administrative access to most features
- `moderator`: Limited administrative access
- `user`: Basic user access

**Response:**
```json
{
  "status": "success",
  "message": "Admin user created successfully",
  "data": {
    "admin_user": {
      "id": 1,
      "user_id": 1,
      "role": "admin",
      "permissions": ["create_user", "read_user", "update_user"],
      "is_active": true,
      "created_by": 1,
      "created_at": "2025-01-01T00:00:00Z"
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 6. Get All Admin Users
```http
GET /dbas/api/admin/admin-users?page=1&limit=50
```

**Response:**
```json
{
  "status": "success",
  "message": "Admin users retrieved successfully",
  "data": {
    "admin_users": [
      {
        "id": 1,
        "user_id": 1,
        "role": "admin",
        "permissions": ["create_user", "read_user", "update_user"],
        "is_active": true,
        "created_by": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-01T00:00:00Z",
        "user": {
          "first_name": "John",
          "last_name": "Doe",
          "email": "john@example.com",
          "username": "johndoe"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 10,
      "pages": 1
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 7. Get Admin User by User ID
```http
GET /dbas/api/admin/admin-users/{user_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Admin user retrieved successfully",
  "data": {
    "admin_user": {
      "id": 1,
      "user_id": 1,
      "role": "admin",
      "permissions": ["create_user", "read_user", "update_user"],
      "is_active": true,
      "created_by": 1,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z",
      "last_login": "2025-01-01T00:00:00Z"
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Analytics

#### 8. Get Analytics
```http
GET /dbas/api/admin/analytics?metric=user_registrations&start_date=2025-01-01&end_date=2025-01-31
```

**Query Parameters:**
- `metric` (required): Metric to analyze
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Available Metrics:**
- `user_registrations`: User registration trends
- `user_logins`: User login trends
- `api_usage`: API usage statistics
- `error_rate`: Error rate analysis
- `response_time`: Response time analysis

**Response:**
```json
{
  "status": "success",
  "message": "Analytics retrieved successfully",
  "data": {
    "metric": "user_registrations",
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T00:00:00Z",
    "data": [
      {
        "date": "2025-01-01",
        "count": 10
      },
      {
        "date": "2025-01-02",
        "count": 15
      }
    ]
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## ⚙️ Settings Management API

### System Settings

#### 1. Get All Settings
```http
GET /dbas/api/settings?category=api
```

**Query Parameters:**
- `category` (optional): Filter by category

**Response:**
```json
{
  "status": "success",
  "message": "Settings retrieved successfully",
  "data": {
    "settings": [
      {
        "id": 1,
        "key": "api_rate_limit",
        "value": "1000",
        "description": "API rate limit per hour",
        "category": "api",
        "is_encrypted": false,
        "is_public": false,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "updated_by": 1
      }
    ],
    "total": 1
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 2. Get Setting by Key
```http
GET /dbas/api/settings/{setting_key}
```

**Response:**
```json
{
  "status": "success",
  "message": "Setting retrieved successfully",
  "data": {
    "setting": {
      "id": 1,
      "key": "api_rate_limit",
      "value": "1000",
      "description": "API rate limit per hour",
      "category": "api",
      "is_encrypted": false,
      "is_public": false,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z",
      "updated_by": 1
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 3. Update Setting
```http
PUT /dbas/api/settings/{setting_key}
```

**Request Body:**
```json
{
  "value": "2000",
  "description": "Updated API rate limit per hour"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Setting updated successfully",
  "data": {
    "message": "Setting updated successfully",
    "key": "api_rate_limit",
    "updated_by": 1
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 4. Get Public Settings
```http
GET /dbas/api/settings/public/
```

**Response:**
```json
{
  "status": "success",
  "message": "Public settings retrieved successfully",
  "data": {
    "settings": [
      {
        "id": 2,
        "key": "app_name",
        "value": "DBAAS Backend",
        "description": "Application name",
        "category": "general",
        "is_encrypted": false,
        "is_public": true,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "updated_by": 1
      }
    ],
    "total": 1
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 5. Get Settings by Category
```http
GET /dbas/api/settings/category/{category}
```

**Response:**
```json
{
  "status": "success",
  "message": "Settings for category 'api' retrieved successfully",
  "data": {
    "settings": [
      {
        "id": 1,
        "key": "api_rate_limit",
        "value": "1000",
        "description": "API rate limit per hour",
        "category": "api",
        "is_encrypted": false,
        "is_public": false,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "updated_by": 1
      }
    ],
    "category": "api",
    "total": 1
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 6. Get Setting Categories
```http
GET /dbas/api/settings/categories
```

**Response:**
```json
{
  "status": "success",
  "message": "Categories retrieved successfully",
  "data": {
    "categories": ["api", "database", "email", "security", "general"],
    "total": 5
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 7. Bulk Update Settings
```http
POST /dbas/api/settings/bulk-update
```

**Request Body:**
```json
[
  {
    "key": "api_rate_limit",
    "value": "2000",
    "description": "Updated API rate limit"
  },
  {
    "key": "max_file_size",
    "value": "10MB",
    "description": "Maximum file upload size"
  }
]
```

**Response:**
```json
{
  "status": "success",
  "message": "Bulk update completed. 2 successful, 0 failed",
  "data": {
    "results": [
      {
        "key": "api_rate_limit",
        "status": "success",
        "message": "Setting updated successfully"
      },
      {
        "key": "max_file_size",
        "status": "success",
        "message": "Setting updated successfully"
      }
    ],
    "errors": [],
    "total_processed": 2,
    "successful": 2,
    "failed": 0
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## 🔒 Permissions & Roles

### User Roles

1. **Super Admin**
   - Full access to all features
   - Can create/delete other admins
   - Can manage all settings
   - All permissions

2. **Admin**
   - User management (create, read, update, delete, ban)
   - Role management (read, assign)
   - Settings management (read, update)
   - Analytics access
   - Log viewing

3. **Moderator**
   - User management (read, update, ban)
   - Role management (read)
   - Settings management (read)
   - Analytics access

4. **User**
   - Basic user access
   - Can only read their own profile

### Available Permissions

- `create_user`: Create new users
- `read_user`: Read user information
- `update_user`: Update user information
- `delete_user`: Delete users
- `ban_user`: Ban users
- `unban_user`: Unban users
- `create_admin`: Create admin users
- `read_admin`: Read admin information
- `update_admin`: Update admin information
- `delete_admin`: Delete admin users
- `create_role`: Create roles
- `read_role`: Read role information
- `update_role`: Update roles
- `delete_role`: Delete roles
- `assign_role`: Assign roles to users
- `read_settings`: Read system settings
- `update_settings`: Update system settings
- `view_analytics`: View analytics data
- `export_data`: Export data
- `manage_api_keys`: Manage API keys
- `view_logs`: View system logs

---

## 🚀 Quick Start Examples

### 1. Get All Users
```bash
curl -X GET "http://localhost:8000/dbas/api/admin/users?page=1&limit=10" \
  -H "Content-Type: application/json"
```

### 2. Ban a User
```bash
curl -X PUT "http://localhost:8000/dbas/api/admin/users/1/status" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "action": "ban",
    "reason": "Violation of terms"
  }'
```

### 3. Create Admin User
```bash
curl -X POST "http://localhost:8000/dbas/api/admin/admin-users" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "role": "admin",
    "permissions": ["create_user", "read_user", "update_user"]
  }'
```

### 4. Get System Settings
```bash
curl -X GET "http://localhost:8000/dbas/api/settings" \
  -H "Content-Type: application/json"
```

### 5. Update Setting
```bash
curl -X PUT "http://localhost:8000/dbas/api/settings/api_rate_limit" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "2000",
    "description": "Updated rate limit"
  }'
```

---

## 📊 Health Checks

### Admin Health Check
```http
GET /dbas/api/admin/health
```

### Settings Health Check
```http
GET /dbas/api/settings/health
```

---

## 🔧 Error Handling

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "message": "Error description",
  "data": null,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

## 🎯 Production Features

✅ **User Management**: Complete CRUD operations for users
✅ **Role-Based Access Control**: Granular permissions system
✅ **Admin Management**: Create and manage admin users
✅ **System Settings**: Configurable application settings
✅ **Analytics**: System usage analytics
✅ **Bulk Operations**: Efficient bulk updates
✅ **Health Monitoring**: Service health checks
✅ **Audit Logging**: Track all admin actions
✅ **Data Validation**: Comprehensive input validation
✅ **Error Handling**: Robust error management

---

**Built with ❤️ using FastAPI and PostgreSQL**
