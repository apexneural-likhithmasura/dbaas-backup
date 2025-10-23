# Complete Authentication API Guide

## Overview

Complete authentication system with **ALL fields available** but only **4 mandatory fields** for signup: `first_name`, `email`, `password`, and `confirm_password`.

---

## 🚀 **Signup API - All Fields Available**

### **Endpoint**: `POST /dbas/api/auth/signup`

### **Field Structure**:

#### **🔴 MANDATORY FIELDS (4 only)**:
```json
{
  "first_name": "Bob",                    // REQUIRED
  "email": "bob.johnson@example.com",     // REQUIRED  
  "password": "SecurePassword123!",       // REQUIRED
  "confirm_password": "SecurePassword123!" // REQUIRED
}
```

#### **🟡 OPTIONAL FIELDS (all available)**:
```json
{
  "last_name": "Johnson",                 // Optional
  "username": "bobjohnson",               // Optional (auto-generated if not provided)
  "phone_number": "+1987654321",          // Optional
  "date_of_birth": "1985-06-20",          // Optional (YYYY-MM-DD format)
  "gender": "male",                       // Optional (male/female/other/prefer_not_to_say)
  "country": "Canada",                    // Optional
  "receive_newsletters": true,            // Optional (default: false)
  "accept_terms": true,                   // Optional (default: true)
  "accept_privacy_policy": true           // Optional (default: true)
}
```

---

## 🧪 **Test Examples**

### **1. Minimal Signup** (Only 4 Mandatory Fields):
```bash
curl -X POST http://localhost:8000/dbas/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "email": "alice.smith@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }'
```

**Response**:
```json
{
  "status": "success",
  "message": "User account created successfully",
  "data": {
    "user": {
      "id": 3,
      "first_name": "Alice",
      "last_name": null,
      "email": "alice.smith@example.com",
      "username": "alice.smith",
      "phone_number": null,
      "date_of_birth": null,
      "gender": null,
      "country": null,
      "receive_newsletters": false,
      "is_active": true,
      "created_at": "2025-10-23T05:48:34.776518"
    },
    "message": "Welcome! Your account has been created successfully."
  }
}
```

### **2. Complete Signup** (All Fields Provided):
```bash
curl -X POST http://localhost:8000/dbas/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Bob",
    "last_name": "Johnson",
    "email": "bob.johnson@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "username": "bobjohnson",
    "phone_number": "+1987654321",
    "date_of_birth": "1985-06-20",
    "gender": "male",
    "country": "Canada",
    "receive_newsletters": true,
    "accept_terms": true,
    "accept_privacy_policy": true
  }'
```

**Response**:
```json
{
  "status": "success",
  "message": "User account created successfully",
  "data": {
    "user": {
      "id": 4,
      "first_name": "Bob",
      "last_name": "Johnson",
      "email": "bob.johnson@example.com",
      "username": "bobjohnson",
      "phone_number": "+1987654321",
      "date_of_birth": "1985-06-20",
      "gender": "male",
      "country": "Canada",
      "receive_newsletters": true,
      "is_active": true,
      "created_at": "2025-10-23T05:48:41.363107"
    },
    "message": "Welcome! Your account has been created successfully."
  }
}
```

---

## 🔐 **Login API** (Unchanged)

### **Endpoint**: `POST /dbas/api/auth/login`

```bash
curl -X POST http://localhost:8000/dbas/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob.johnson@example.com",
    "password": "SecurePassword123!"
  }'
```

---

## 📊 **Field Details**

### **Mandatory Fields** (4):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `first_name` | string | 1-50 chars | User's first name |
| `email` | string | Valid email | User's email address |
| `password` | string | 8+ chars, complex | User's password |
| `confirm_password` | string | Must match password | Password confirmation |

### **Optional Fields** (9):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `last_name` | string | null | User's last name |
| `username` | string | auto-generated | Unique username |
| `phone_number` | string | null | Phone number |
| `date_of_birth` | string | null | Date in YYYY-MM-DD format |
| `gender` | string | null | male/female/other/prefer_not_to_say |
| `country` | string | null | User's country |
| `receive_newsletters` | boolean | false | Newsletter subscription |
| `accept_terms` | boolean | true | Terms acceptance |
| `accept_privacy_policy` | boolean | true | Privacy policy acceptance |

---

## ✨ **Smart Features**

### **Auto-Generated Username**:
- If no username provided → generated from email
- Example: `alice.smith@example.com` → username: `alice.smith`
- If username exists → adds number: `alice.smith1`, `alice.smith2`, etc.

### **Smart Defaults**:
- `last_name`: null if not provided
- `accept_terms`: defaults to `true`
- `accept_privacy_policy`: defaults to `true`
- `receive_newsletters`: defaults to `false`

### **Password Requirements**:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character

---

## 📊 **Current Users in Database**

1. **John Doe** (ID: 1)
   - Email: `john.doe@example.com`
   - Username: `johndoe123`

2. **Praveen** (ID: 2)
   - Email: `praveen.jogi@example.com`
   - Username: `praveen.jogi` (auto-generated)

3. **Alice** (ID: 3)
   - Email: `alice.smith@example.com`
   - Username: `alice.smith` (auto-generated)
   - Minimal signup (4 fields only)

4. **Bob Johnson** (ID: 4)
   - Email: `bob.johnson@example.com`
   - Username: `bobjohnson`
   - Complete signup (all fields)

---

## 🎯 **All Available Endpoints**

1. **POST `/dbas/api/auth/signup`** - Create account (4 mandatory, 9 optional)
2. **POST `/dbas/api/auth/login`** - Login user
3. **GET `/dbas/api/auth/user/{user_id}`** - Get user profile
4. **GET `/dbas/api/auth/health/check`** - Service health

---

## 🌐 **Interactive Testing**

Visit: **http://localhost:8000/dbas/api/docs**

Test both minimal and complete signup forms!

---

## ✅ **Status**

- ✅ **All Fields Available**: 13 total fields (4 mandatory + 9 optional)
- ✅ **Flexible Signup**: Can use 4 fields or all 13 fields
- ✅ **Auto Username**: Generated from email when not provided
- ✅ **Smart Defaults**: All optional fields handled gracefully
- ✅ **Login Working**: Authentication successful for all users
- ✅ **Database Updated**: Users table with complete structure

---

**Complete authentication system is ready!** 🎉

**Minimum required**: `first_name`, `email`, `password`, `confirm_password`  
**Maximum available**: All 13 fields for complete user profiles
