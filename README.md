# Procure-to-Pay System

A complete Procure-to-Pay system similar to Payhawk, built with Django REST Framework (backend) and Next.js/React (frontend).

## Features

- **Multi-level Approval Workflow**: Staff create requests → Level 1 Approver → Level 2 Approver → Finance
- **Document Processing**: Automatic extraction from proforma invoices, PO generation, and receipt validation
- **Role-based Access Control**: Different permissions for staff, approvers, and finance users
- **JWT Authentication**: Secure token-based authentication
- **File Uploads**: Support for proforma, purchase order, and receipt files
- **RESTful API**: Complete API with Swagger/OpenAPI documentation

## Tech Stack

### Backend

- Django 4.2.7
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Docker & Docker Compose
- Document processing (pdfplumber, PyPDF2, OCR)

### Frontend

- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- React Query
- Axios

## Project Structure

```
procure-to-pay-system/
├── server/                 # Django backend
│   ├── config/            # Django settings, URLs, WSGI/ASGI
│   ├── core/              # User model, authentication, permissions
│   ├── requests/          # Purchase requests app
│   │   ├── doc_processing/  # Document processing utilities
│   │   ├── models.py      # PurchaseRequest, Approval, RequestItem
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── client/                # Next.js frontend
│   ├── app/               # Next.js app directory
│   ├── lib/               # API client, types
│   └── package.json
└── docs/                  # Documentation
    └── postman_collection.json
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Backend Setup (Docker)

1. **Navigate to server directory:**

   ```bash
   cd server
   ```

2. **Create environment file:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your settings if needed.

3. **Build and start services:**

   ```bash
   docker-compose up --build
   ```

   This will:

   - Start PostgreSQL database
   - Start Redis (optional)
   - Build and start Django application
   - Run migrations automatically
   - Collect static files

4. **Create superuser (optional):**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the API:**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - Swagger UI: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/

### Backend Setup (Local Development)

1. **Create virtual environment:**

   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database:**

   - **Option A (Local):** Create database: `procure_to_pay` and update `.env` with credentials
   - **Option B (Neon):** See `docs/NEON_SETUP.md` for connecting to Neon PostgreSQL

4. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to client directory:**

   ```bash
   cd client
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Set environment variable (optional):**
   Create `.env.local`:

   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. **Run development server:**

   ```bash
   npm run dev
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000

## User Roles

The system supports four user roles:

1. **staff**: Can create purchase requests and view their own requests
2. **approver_level_1**: Can approve/reject requests (first level)
3. **approver_level_2**: Can approve/reject requests (second level)
4. **finance**: Can view all requests and validate receipts

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout (blacklist token)
- `GET /api/auth/me/` - Get current user info

### Purchase Requests

- `GET /api/requests/` - List requests (filtered by role)
- `GET /api/requests/{id}/` - Get request details
- `POST /api/requests/` - Create new request (staff only)
- `PUT /api/requests/{id}/` - Update request (if pending)
- `PATCH /api/requests/{id}/approve/` - Approve request (approvers)
- `PATCH /api/requests/{id}/reject/` - Reject request (approvers)
- `POST /api/requests/{id}/submit-receipt/` - Submit receipt file
- `POST /api/requests/{id}/validate-receipt/` - Validate receipt (finance)

### Documentation

- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc
- `GET /api/openapi/` - OpenAPI JSON schema

## Workflow

1. **Staff creates request** → Status: `PENDING`
2. **Level 1 Approver reviews** → Approves/Rejects
3. **Level 2 Approver reviews** → Approves/Rejects
4. **If both approve** → Status: `APPROVED` → PO auto-generated
5. **If any reject** → Status: `REJECTED`
6. **Staff submits receipt** → Receipt file uploaded
7. **Finance validates** → Compares receipt with PO

## Document Processing

The system includes utilities for:

1. **Proforma Extraction**: Extracts vendor, items, and totals from PDF/image files
2. **PO Generation**: Automatically generates Purchase Orders (PDF/JSON) upon approval
3. **Receipt Validation**: Compares receipt data with PO to detect discrepancies

## Testing with Postman

Import the Postman collection from `docs/postman_collection.json`:

1. Open Postman
2. Import → File → Select `docs/postman_collection.json`
3. Set `base_url` variable to `http://localhost:8000/api`
4. Login first to get `access_token` (automatically set)
5. Use other endpoints with authentication

## Production Deployment

### Environment Variables

Update `.env` with production values:

- `DEBUG=False`
- `SECRET_KEY` (generate strong secret key)
- `ALLOWED_HOSTS` (your domain)
- Database credentials
- CORS allowed origins

### Docker Production

1. Update `docker-compose.yml` for production settings
2. Use production database (managed service recommended)
3. Set up reverse proxy (nginx) for static files
4. Configure SSL/TLS certificates
5. Set up monitoring and logging

### Frontend Production

1. Build the application:

   ```bash
   npm run build
   ```

2. Deploy to Vercel, Netlify, or your preferred hosting

## Development Notes

- The system uses Django signals to auto-generate POs when requests are approved
- Approval records are created on-demand when approvers act
- File uploads are stored in `media/` directory
- Static files are collected to `staticfiles/` directory

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify network connectivity in Docker

### File Upload Issues

- Check `MEDIA_ROOT` permissions
- Ensure sufficient disk space
- Verify file size limits in settings

### Frontend API Connection

- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in Django
- Ensure backend is running

## License

Copyright (c) 2025 Y-elv

Permission is granted to use this software only. For copying, modifying, or distributing this software, you must request and obtain permission from the copyright holder. This software is provided "as is" without warranty of any kind.

**Open Source Usage**: This software is open to open source use, but permission must be requested and obtained before use. When using this software in open source projects, you must:
- Request permission from the copyright holder
- Include proper attribution and copyright notice
- Copy and maintain this license notice in all copies or substantial portions of the software

## Support

For issues or questions, please check the API documentation at `/api/docs/` or review the code comments.
