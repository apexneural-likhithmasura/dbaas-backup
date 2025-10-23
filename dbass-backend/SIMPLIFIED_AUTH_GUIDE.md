# Simplified Authentication API Guide

## Overview

Simplified authentication system with **only 4 mandatory fields** for signup: **first_name**, **email**, **password**, and **confirm_password**.

---

## 🚀 **Simplified Signup API**

### **Endpoint**: `POST /dbas/api/auth/signup`

### **Mandatory Fields Only**:

```json
{
  "first_name": "Praveen",
  "email": "praveen.jogi@example.com", 
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```

### **Optional Fields** (with defaults):
- `last_name`: null (optional)
- `username`: auto-generated from email (optional)
- `phone_number`: null (optional)
- `date_of_birth`: null (optional)
- `gender`: null (optional)
- `country`: null (optional)
- `receive_newsletters`: false (default)
- `accept_terms`: true (default)
- `accept_privacy_policy`: true (default)

---

## 🧪 **Test Examples**

### **Minimal Signup** (Only Required Fields):
```bash
curl -X POST http://localhost:8000/dbas/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Praveen",
    "email": "praveen.jogi@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }'
```

### **Response**:
```json
{
  "status": "success",
  "message": "User account created successfully",
  "data": {
    "user": {
      "id": 2,
      "first_name": "Praveen",
      "last_name": null,
      "email": "praveen.jogi@example.com",
      "username": "praveen.jogi",
      "phone_number": null,
      "date_of_birth": null,
      "gender": null,
      "country": null,
      "receive_newsletters": false,
      "is_active": true,
      "created_at": "2025-10-23T05:45:03.424544"
    },
    "message": "Welcome! Your account has been created successfully."
  },
  "timestamp": "2025-10-23T05:45:03.741160"
}
```

---

## 🔐 **Login API** (Unchanged)

### **Endpoint**: `POST /dbas/api/auth/login`

```bash
curl -X POST http://localhost:8000/dbas/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "praveen.jogi@example.com",
    "password": "SecurePassword123!"
  }'
```

### **Response**:
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": 2,
      "first_name": "Praveen",
      "last_name": "",
      "email": "praveen.jogi@example.com",
      "username": "praveen.jogi",
      "phone_number": null,
      "date_of_birth": null,
      "gender": null,
      "country": null,
      "receive_newsletters": false,
      "is_active": true,
      "created_at": "2025-10-23T05:45:03.424544",
      "updated_at": "2025-10-23T05:45:03.424551",
      "last_login": "2025-10-23T05:46:28.013660"
    },
    "message": "Welcome back! You have been logged in successfully."
  },
  "timestamp": "2025-10-23T05:46:28.051522"
}
```

---

## ✨ **Key Features**

### **Auto-Generated Username**:
- If no username provided, it's auto-generated from email
- Example: `praveen.jogi@example.com` → username: `praveen.jogi`
- If username exists, adds number: `praveen.jogi1`, `praveen.jogi2`, etc.

### **Smart Defaults**:
- `last_name`: Empty string if not provided
- `accept_terms`: Defaults to `true`
- `accept_privacy_policy`: Defaults to `true`
- `receive_newsletters`: Defaults to `false`

### **Password Requirements** (Still Enforced):
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

---

## 🎯 **All Available Endpoints**

1. **POST `/dbas/api/auth/signup`** - Create account (4 fields only!)
2. **POST `/dbas/api/auth/login`** - Login user
3. **GET `/dbas/api/auth/user/{user_id}`** - Get user profile
4. **GET `/dbas/api/auth/health/check`** - Service health

---

## 🌐 **Interactive Testing**

Visit: **http://localhost:8000/dbas/api/docs**

Test the simplified signup form with just the 4 mandatory fields!

---

## ✅ **Status**

- ✅ **Simplified Signup**: Only 4 mandatory fields
- ✅ **Auto Username**: Generated from email
- ✅ **Smart Defaults**: All optional fields handled
- ✅ **Login Working**: Authentication successful
- ✅ **Database Updated**: Users table with new structure

---

**Simplified authentication system is ready!** 🎉

**Minimum required for signup**: `first_name`, `email`, `password`, `confirm_password`
