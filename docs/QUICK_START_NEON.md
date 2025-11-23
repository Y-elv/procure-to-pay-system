# Quick Start: Connect to Neon PostgreSQL

## When to Connect

**Connect to Neon BEFORE running migrations for the first time.**

## 3 Simple Steps

### 1. Get Your Neon Connection String

From Neon Console → Your Project → Connection Details:
```
postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

### 2. Update Your `.env` File

In `server/.env`, add:

```env
# Option 1: Use full connection string (easiest)
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Option 2: Or use individual components
DB_HOST=ep-xxx-xxx.us-east-2.aws.neon.tech
DB_NAME=your_db_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

### 3. Test and Run Migrations

```bash
# Test connection
python manage.py dbshell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## That's It! ✅

Your Django app is now connected to Neon PostgreSQL.

## Need More Details?

See the full guide: `docs/NEON_SETUP.md`

