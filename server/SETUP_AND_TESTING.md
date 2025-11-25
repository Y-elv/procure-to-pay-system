# Setup and Testing Guide

## Step-by-Step Instructions to Run Django Server and Verify Endpoints

### Prerequisites

1. Python 3.8+ installed
2. PostgreSQL database (Neon or local)
3. Virtual environment (recommended)

### Step 1: Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Ensure your `.env` file in the `server/` directory contains:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_NAME=neondb
DATABASE_USER=abc
DATABASE_PASSWORD=npgxxxx
DATABASE_HOST=ep-square-mode-adqo44y4-pooler.c-2.us-east-1.aws-neon.tech
DATABASE_PORT=5432
DATABASE_SSLMODE=require
DATABASE_CHANNEL_BINDING=require
APP_PORT=8001
```

### Step 3: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 5: Start the Django Server

```bash
python manage.py runserver
```

You should see:
```
DB connected
🚀 Django server is running on http://localhost:8001
```

The server will start on port 8001 (or the port specified in `APP_PORT`).

### Step 6: Access Swagger UI

Open your browser and navigate to:
- **Swagger UI**: `http://localhost:8001/swagger/`
- **ReDoc**: `http://localhost:8001/redoc/`

### Step 7: Test Authentication Endpoints

#### 7.1 Register a User

In Swagger UI, find the `POST /api/auth/register/` endpoint:

1. Click "Try it out"
2. Enter request body:
```json
{
  "username": "test_staff",
  "email": "staff@example.com",
  "password": "testpass123",
  "password_confirm": "testpass123",
  "role": "staff",
  "first_name": "Test",
  "last_name": "Staff"
}
```
3. Click "Execute"
4. Copy the `access` token from the response

#### 7.2 Authorize in Swagger

1. Click the "Authorize" button (top right)
2. Enter: `Bearer <your_access_token>`
3. Click "Authorize"
4. Click "Close"

Now all authenticated endpoints will use this token.

#### 7.3 Test Login

1. Find `POST /api/auth/login/`
2. Enter credentials:
```json
{
  "username": "test_staff",
  "password": "testpass123"
}
```
3. Execute and verify you receive tokens

### Step 8: Test Purchase Request Endpoints

#### 8.1 Create a Purchase Request (Staff)

1. Find `POST /api/requests/`
2. Click "Try it out"
3. Enter request body:
```json
{
  "title": "Office Supplies Q1",
  "description": "Purchase office supplies for first quarter",
  "amount": "1500.00",
  "items": [
    {
      "item_name": "Printer Paper",
      "quantity": 10,
      "price": "25.00"
    },
    {
      "item_name": "Pens",
      "quantity": 50,
      "price": "2.00"
    }
  ]
}
```
4. Execute
5. Note the `id` from the response

#### 8.2 View Request Detail

1. Find `GET /api/requests/{id}/`
2. Enter the request ID from step 8.1
3. Execute and verify the response

#### 8.3 List Requests

1. Find `GET /api/requests/`
2. Try query parameters:
   - `status=pending`
   - `search=office`
   - `ordering=-created_at`
3. Execute and verify paginated results

### Step 9: Test Approval Workflow

#### 9.1 Create Approver Users

Register two approver users:

**Level 1 Approver:**
```json
{
  "username": "approver1",
  "email": "approver1@example.com",
  "password": "testpass123",
  "password_confirm": "testpass123",
  "role": "approver_level_1",
  "first_name": "Approver",
  "last_name": "One"
}
```

**Level 2 Approver:**
```json
{
  "username": "approver2",
  "email": "approver2@example.com",
  "password": "testpass123",
  "password_confirm": "testpass123",
  "role": "approver_level_2",
  "first_name": "Approver",
  "last_name": "Two"
}
```

#### 9.2 Approve Request (Level 1)

1. Login as `approver1` and get token
2. Authorize with the new token in Swagger
3. Find `PATCH /api/requests/{id}/approve/`
4. Enter request ID and body:
```json
{
  "comment": "Approved - within budget"
}
```
5. Execute
6. Verify status is still `pending` (waiting for Level 2)

#### 9.3 Approve Request (Level 2)

1. Login as `approver2` and get token
2. Authorize with the new token
3. Find `PATCH /api/requests/{id}/approve/`
4. Enter same request ID and body:
```json
{
  "comment": "Approved - looks good"
}
```
5. Execute
6. Verify status is now `approved`

#### 9.4 List Pending Requests

1. As approver, find `GET /api/requests/pending/`
2. Execute
3. Verify only pending requests are returned

#### 9.5 List Reviewed Requests

1. Find `GET /api/requests/reviewed/`
2. Try with query parameter: `my_reviews=true`
3. Execute
4. Verify reviewed requests are returned

### Step 10: Test Receipt Submission and Validation

#### 10.1 Submit Receipt (Staff)

1. Login as staff user
2. Find `POST /api/requests/{id}/submit_receipt/`
3. Enter request ID (must be approved)
4. Upload receipt file (if you have one)
5. Execute

#### 10.2 Validate Receipt (Finance)

1. Register a finance user:
```json
{
  "username": "finance_user",
  "email": "finance@example.com",
  "password": "testpass123",
  "password_confirm": "testpass123",
  "role": "finance",
  "first_name": "Finance",
  "last_name": "User"
}
```

2. Login as finance user and get token
3. Authorize with finance token
4. Find `POST /api/requests/{id}/validate_receipt/`
5. Enter request ID (must have receipt)
6. Execute
7. Verify validation result

### Step 11: Test Error Cases

#### 11.1 Unauthorized Access

1. Click "Authorize" and remove token
2. Try accessing any authenticated endpoint
3. Verify 401 Unauthorized response

#### 11.2 Permission Denied

1. As staff user, try to approve a request
2. Verify 403 Forbidden response

#### 11.3 Invalid Data

1. Try creating request with invalid data
2. Verify 400 Bad Request with validation errors

### Step 12: Verify All Endpoints in Swagger

Go through each endpoint in Swagger UI and verify:

**Authentication:**
- ✅ POST /api/auth/register/
- ✅ POST /api/auth/login/
- ✅ POST /api/auth/logout/
- ✅ GET /api/auth/me/
- ✅ GET /api/auth/users/

**Purchase Requests:**
- ✅ GET /api/requests/
- ✅ POST /api/requests/
- ✅ GET /api/requests/{id}/
- ✅ PATCH /api/requests/{id}/
- ✅ PUT /api/requests/{id}/
- ✅ DELETE /api/requests/{id}/
- ✅ PATCH /api/requests/{id}/approve/
- ✅ PATCH /api/requests/{id}/reject/
- ✅ GET /api/requests/pending/
- ✅ GET /api/requests/reviewed/
- ✅ POST /api/requests/{id}/submit_receipt/
- ✅ POST /api/requests/{id}/validate_receipt/

### Step 13: Test with Different Roles

Create test users for each role and verify:

1. **Staff**: Can create, view own, update own pending, submit receipts
2. **Approver Level 1**: Can view all, list pending/reviewed, approve/reject
3. **Approver Level 2**: Can view all, list pending/reviewed, approve/reject
4. **Finance**: Can view all, list pending/reviewed, validate receipts

### Troubleshooting

#### Database Connection Error

If you see "DB connected" error:
1. Check `.env` file has correct database credentials
2. Verify database is accessible
3. Check SSL settings match your database provider

#### Port Already in Use

If port 8001 is in use:
1. Change `APP_PORT` in `.env`
2. Restart server

#### Migration Errors

If migrations fail:
```bash
python manage.py migrate --run-syncdb
```

#### Swagger Not Loading

If Swagger UI doesn't load:
1. Check `drf-yasg` is installed: `pip install drf-yasg`
2. Verify URLs are correct in `config/urls.py`
3. Check server logs for errors

### Next Steps

1. Review `API_DOCUMENTATION.md` for complete endpoint reference
2. Test all endpoints with different user roles
3. Verify business logic (approval workflow, status changes)
4. Test file uploads (proforma, receipt)
5. Test pagination, filtering, and search

### Additional Resources

- Django REST Framework: https://www.django-rest-framework.org/
- DRF-YASG (Swagger): https://drf-yasg.readthedocs.io/
- JWT Authentication: https://django-rest-framework-simplejwt.readthedocs.io/

