# Connecting to Neon PostgreSQL Database

This guide will help you connect your Procure-to-Pay system to a Neon PostgreSQL database.

## When to Connect to Neon

You should set up the Neon database connection **before** running migrations for the first time. Here's the recommended workflow:

1. ✅ Create Neon database account
2. ✅ Get connection credentials
3. ✅ Update environment variables
4. ✅ Test connection
5. ✅ Run migrations
6. ✅ Create superuser
7. ✅ Start using the application

## Step-by-Step Setup

### 1. Create Neon Database

1. Go to [Neon Console](https://console.neon.tech/)
2. Sign up or log in
3. Create a new project
4. Create a new database (or use the default one)

### 2. Get Connection String

In your Neon dashboard:

1. Go to your project
2. Click on "Connection Details" or "Connection String"
3. You'll see connection details like:
   ```
   postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```

### 3. Update Environment Variables

#### Option A: Using Connection String (Recommended)

Update your `server/.env` file:

```env
# Neon Database Connection
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Or use individual components:
DB_NAME=your_db_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=ep-xxx-xxx.us-east-2.aws.neon.tech
DB_PORT=5432
```

**Important Notes:**
- Neon requires SSL connections, so `sslmode=require` is necessary
- The host format is `ep-xxx-xxx.region.aws.neon.tech`
- Default port is 5432

#### Option B: Update Docker Compose (if using Docker)

Update `server/docker-compose.yml`:

```yaml
services:
  web:
    environment:
      - DB_NAME=${DB_NAME:-your_neon_db_name}
      - DB_USER=${DB_USER:-your_neon_username}
      - DB_PASSWORD=${DB_PASSWORD:-your_neon_password}
      - DB_HOST=${DB_HOST:-ep-xxx-xxx.us-east-2.aws.neon.tech}
      - DB_PORT=5432
```

### 4. Update Django Settings for Neon

The current `settings.py` already supports environment variables. However, for Neon, you may want to add SSL configuration:

```python
# In server/config/settings.py, update DATABASES section:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'procure_to_pay'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Required for Neon
        },
    }
}
```

### 5. Install Required Package (if needed)

Ensure `psycopg2-binary` is installed (already in requirements.txt):

```bash
pip install psycopg2-binary
```

### 6. Test Connection

#### Local Development:

```bash
cd server
python manage.py dbshell
```

If it connects successfully, you'll see the PostgreSQL prompt.

#### Or test with Python:

```bash
python manage.py shell
```

```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
```

### 7. Run Migrations

Once connected, run migrations:

```bash
# Local
python manage.py migrate

# Docker
docker-compose exec web python manage.py migrate
```

### 8. Create Superuser

```bash
# Local
python manage.py createsuperuser

# Docker
docker-compose exec web python manage.py createsuperuser
```

## Docker Setup with Neon

If you're using Docker and want to connect to Neon instead of the local PostgreSQL container:

### Option 1: Remove Local DB, Use Neon Only

1. Comment out or remove the `db` service from `docker-compose.yml`
2. Update environment variables to point to Neon
3. Remove the `depends_on: db` from the web service

```yaml
services:
  # db:
  #   image: postgres:15-alpine
  #   ... (comment out or remove)

  web:
    # Remove: depends_on: db
    environment:
      - DB_HOST=ep-xxx-xxx.us-east-2.aws.neon.tech
      - DB_NAME=your_db_name
      - DB_USER=your_username
      - DB_PASSWORD=your_password
      - DB_PORT=5432
```

### Option 2: Keep Local DB for Development, Use Neon for Production

Use different `.env` files:
- `.env.development` - local PostgreSQL
- `.env.production` - Neon PostgreSQL

## Connection Pooling (Optional)

Neon supports connection pooling. If you expect high traffic, consider using Neon's connection pooler:

1. In Neon dashboard, go to "Connection Pooling"
2. Enable pooling
3. Use the pooled connection string (usually has `-pooler` in the hostname)

Example pooled connection:
```
postgresql://username:password@ep-xxx-xxx-pooler.us-east-2.aws.neon.tech/dbname?sslmode=require
```

## Troubleshooting

### SSL Connection Error

If you get SSL errors:
- Ensure `sslmode=require` is in your connection string
- Check that your Django settings include SSL options

### Connection Timeout

- Verify your IP is not blocked (Neon allows all IPs by default)
- Check firewall settings
- Ensure the hostname is correct

### Authentication Failed

- Double-check username and password
- Ensure the database name is correct
- Verify credentials in Neon dashboard

### Docker Connection Issues

- Ensure environment variables are set correctly
- Check that the web container can reach the internet
- Verify DNS resolution works in the container

## Security Best Practices

1. **Never commit credentials** - Use `.env` files (already in `.gitignore`)
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate passwords regularly** - Update credentials in Neon dashboard
4. **Use connection pooling** - For production workloads
5. **Enable SSL** - Always required for Neon

## Next Steps

After connecting to Neon:

1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Create superuser: `python manage.py createsuperuser`
3. ✅ Test API endpoints
4. ✅ Create test users with different roles
5. ✅ Start using the application!

## Quick Reference

**Neon Dashboard:** https://console.neon.tech/
**Neon Docs:** https://neon.tech/docs/
**Connection String Format:** `postgresql://user:pass@host:port/dbname?sslmode=require`

