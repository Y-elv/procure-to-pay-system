# Procure-to-Pay System - Complete API Documentation

## Overview

This document provides a complete reference for all API endpoints in the Procure-to-Pay system, including authentication, role-based access control, and business workflow endpoints.

## Base URL

- Development: `http://localhost:8001/api`
- Production: Configure via `ALLOWED_HOSTS` in settings

## Authentication

All endpoints (except registration and login) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## API Documentation UI

- **Swagger UI**: `http://localhost:8001/swagger/`
- **ReDoc**: `http://localhost:8001/redoc/`
- **OpenAPI JSON**: `http://localhost:8001/api/openapi/`

---

## Authentication Endpoints

### 1. Register User
**POST** `/api/auth/register/`

Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "role": "staff",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-01-15T10:30:00Z"
  }
}
```

**Roles:** `staff`, `approver_level_1`, `approver_level_2`, `finance`

---

### 2. Login
**POST** `/api/auth/login/`

Login and receive JWT tokens.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-01-15T10:30:00Z"
  }
}
```

---

### 3. Logout
**POST** `/api/auth/logout/`

Logout and blacklist refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out."
}
```

**Authentication:** Required

---

### 4. Get Current User
**GET** `/api/auth/me/`

Get current authenticated user information.

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "staff",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2025-01-15T10:30:00Z"
}
```

**Authentication:** Required

---

### 5. List Users
**GET** `/api/auth/users/`

List all users (for admin/approvers).

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-01-15T10:30:00Z"
  }
]
```

**Authentication:** Required

---

## Purchase Request Endpoints

### 1. List Purchase Requests
**GET** `/api/requests/`

List purchase requests. Results are filtered based on user role:
- **Staff**: Only their own requests
- **Approvers/Finance**: All requests

**Query Parameters:**
- `status`: Filter by status (`pending`, `approved`, `rejected`)
- `created_by`: Filter by creator ID
- `search`: Search in title and description
- `ordering`: Order by field (`created_at`, `updated_at`, `amount`)
- `page`: Page number (pagination)

**Response (200):**
```json
{
  "count": 10,
  "next": "http://localhost:8001/api/requests/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Office Supplies",
      "description": "Purchase office supplies for Q1",
      "amount": "1500.00",
      "status": "pending",
      "created_by": 1,
      "created_by_username": "john_doe",
      "created_by_name": "John Doe",
      "proforma_file": null,
      "purchase_order_file": null,
      "receipt_file": null,
      "items": [],
      "approvals": [],
      "can_edit": true,
      "can_approve": true,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**Authentication:** Required

**Roles:**
- Staff: Own requests only
- Approvers/Finance: All requests

---

### 2. Get Purchase Request Detail
**GET** `/api/requests/{id}/`

Get detailed information about a specific purchase request.

**Response (200):**
```json
{
  "id": 1,
  "title": "Office Supplies",
  "description": "Purchase office supplies for Q1",
  "amount": "1500.00",
  "status": "pending",
  "created_by": 1,
  "created_by_username": "john_doe",
  "created_by_name": "John Doe",
  "proforma_file": "/media/proformas/1/invoice.pdf",
  "purchase_order_file": null,
  "receipt_file": null,
  "items": [
    {
      "id": 1,
      "item_name": "Printer Paper",
      "quantity": 10,
      "price": "25.00",
      "total": "250.00"
    }
  ],
  "approvals": [
    {
      "id": 1,
      "approver": 2,
      "approver_username": "approver1",
      "approver_name": "Approver One",
      "level": 1,
      "status": "pending",
      "comment": "",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "can_edit": true,
  "can_approve": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Authentication:** Required

**Roles:**
- Staff: Own requests only
- Approvers/Finance: All requests

---

### 3. Create Purchase Request
**POST** `/api/requests/`

Create a new purchase request. Only staff can create requests.

**Request Body:**
```json
{
  "title": "Office Supplies",
  "description": "Purchase office supplies for Q1",
  "amount": "1500.00",
  "proforma_file": "<file>",
  "items": [
    {
      "item_name": "Printer Paper",
      "quantity": 10,
      "price": "25.00"
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Office Supplies",
  "description": "Purchase office supplies for Q1",
  "amount": "1500.00",
  "status": "pending",
  "created_by": 1,
  "created_by_username": "john_doe",
  "created_by_name": "John Doe",
  "proforma_file": "/media/proformas/1/invoice.pdf",
  "purchase_order_file": null,
  "receipt_file": null,
  "items": [...],
  "approvals": [],
  "can_edit": true,
  "can_approve": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Authentication:** Required

**Roles:** Staff only

---

### 4. Update Purchase Request
**PATCH** `/api/requests/{id}/` or **PUT** `/api/requests/{id}/`

Update a purchase request. Only pending requests can be updated. Only the creator can update their own requests.

**Request Body:**
```json
{
  "title": "Updated Office Supplies",
  "description": "Updated description",
  "amount": "2000.00",
  "items": [
    {
      "item_name": "Printer Paper",
      "quantity": 20,
      "price": "25.00"
    }
  ]
}
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Updated Office Supplies",
  ...
}
```

**Authentication:** Required

**Roles:** Staff (own requests only, pending status only)

---

### 5. Delete Purchase Request
**DELETE** `/api/requests/{id}/`

Delete a purchase request. Only pending requests can be deleted.

**Response (204):** No content

**Authentication:** Required

**Roles:** Staff (own requests only)

---

### 6. Approve Purchase Request
**PATCH** `/api/requests/{id}/approve/`

Approve a purchase request. Creates or updates approval record for the approver's level.

**Request Body:**
```json
{
  "comment": "Approved - within budget"
}
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Office Supplies",
  "status": "pending",  // or "approved" if both levels approved
  "approvals": [
    {
      "id": 1,
      "approver": 2,
      "level": 1,
      "status": "approved",
      "comment": "Approved - within budget",
      ...
    }
  ],
  ...
}
```

**Authentication:** Required

**Roles:** `approver_level_1`, `approver_level_2`

**Business Logic:**
- Level 1 approver approves → Request remains pending until Level 2 approves
- Level 2 approver approves → If Level 1 also approved, request status becomes `approved`
- If any approver rejects → Request status becomes `rejected`

---

### 7. Reject Purchase Request
**PATCH** `/api/requests/{id}/reject/`

Reject a purchase request. Comment is required.

**Request Body:**
```json
{
  "comment": "Rejected - exceeds budget limit"
}
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Office Supplies",
  "status": "rejected",
  "approvals": [
    {
      "id": 1,
      "approver": 2,
      "level": 1,
      "status": "rejected",
      "comment": "Rejected - exceeds budget limit",
      ...
    }
  ],
  ...
}
```

**Authentication:** Required

**Roles:** `approver_level_1`, `approver_level_2`

---

### 8. List Pending Requests
**GET** `/api/requests/pending/`

List all pending requests awaiting approval. Available to approvers.

**Query Parameters:** Same as list endpoint (filter, search, ordering, pagination)

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "title": "Office Supplies",
      "status": "pending",
      ...
    }
  ]
}
```

**Authentication:** Required

**Roles:** `approver_level_1`, `approver_level_2`, `finance`

---

### 9. List Reviewed Requests
**GET** `/api/requests/reviewed/`

List reviewed requests (approved or rejected). Available to approvers.

**Query Parameters:**
- `my_reviews=true`: Filter to show only requests reviewed by current user
- Other filters same as list endpoint

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "title": "Office Supplies",
      "status": "approved",
      ...
    }
  ]
}
```

**Authentication:** Required

**Roles:** `approver_level_1`, `approver_level_2`, `finance`

---

### 10. Submit Receipt
**POST** `/api/requests/{id}/submit_receipt/`

Submit receipt file for an approved purchase request. Only the request creator can submit receipts.

**Request Body (multipart/form-data):**
```
receipt_file: <file>
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Office Supplies",
  "status": "approved",
  "receipt_file": "/media/receipts/1/receipt.pdf",
  ...
}
```

**Authentication:** Required

**Roles:** Staff (own requests only, approved status only)

---

### 11. Validate Receipt
**POST** `/api/requests/{id}/validate_receipt/`

Validate receipt against purchase order. Only finance users can validate receipts.

**Response (200):**
```json
{
  "id": 1,
  "is_valid": true,
  "discrepancy_amount": null,
  "discrepancy_details": {},
  "validated_by": 3,
  "validated_by_username": "finance_user",
  "validated_at": "2025-01-15T12:00:00Z"
}
```

**Authentication:** Required

**Roles:** Finance only

---

## Role-Based Access Summary

### Staff (`staff`)
- ✅ Create request
- ✅ List own requests
- ✅ View request detail (own)
- ✅ Update pending request (own)
- ✅ Submit receipt (own, approved only)

### Approver Level 1 (`approver_level_1`)
- ✅ List all requests
- ✅ View request detail (all)
- ✅ List pending requests
- ✅ List reviewed requests
- ✅ Approve/reject requests (Level 1)

### Approver Level 2 (`approver_level_2`)
- ✅ List all requests
- ✅ View request detail (all)
- ✅ List pending requests
- ✅ List reviewed requests
- ✅ Approve/reject requests (Level 2)

### Finance (`finance`)
- ✅ List all requests
- ✅ View request detail (all)
- ✅ List pending requests
- ✅ List reviewed requests
- ✅ Validate receipts

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Only approvers can view pending requests."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## Workflow Example

1. **Staff creates request** → `POST /api/requests/`
   - Status: `pending`
   - Creates approval records for Level 1 and Level 2

2. **Level 1 Approver reviews** → `PATCH /api/requests/{id}/approve/`
   - Status: `pending` (waiting for Level 2)

3. **Level 2 Approver reviews** → `PATCH /api/requests/{id}/approve/`
   - Status: `approved` (if both approved)
   - Auto-generates Purchase Order

4. **Staff submits receipt** → `POST /api/requests/{id}/submit_receipt/`
   - Uploads receipt file

5. **Finance validates** → `POST /api/requests/{id}/validate_receipt/`
   - Compares receipt with PO
   - Returns validation result

---

## Testing with Swagger UI

1. Start the Django server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: `http://localhost:8001/swagger/`

3. Click "Authorize" button and enter:
   ```
   Bearer <your_access_token>
   ```

4. Test endpoints directly from Swagger UI

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- File uploads use multipart/form-data
- Pagination: 20 items per page (configurable)
- Search: Searches in `title` and `description` fields
- Filtering: Available on `status` and `created_by` fields
- Ordering: Available on `created_at`, `updated_at`, `amount`

