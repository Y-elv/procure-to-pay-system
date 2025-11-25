# Check drf_yasg Format Attributes (Django Shell Method)

## Problem
Using `python -c "..."` triggers "Apps aren't loaded yet" error because Django apps aren't initialized.

## Solution
Use `python manage.py shell` which properly initializes Django before running code.

## Quick One-Liner (Copy-Paste Ready)

Run this from the `server` directory:

```powershell
if (Test-Path "venv\Scripts\Activate.ps1") { & .\venv\Scripts\Activate.ps1 }; $env:DJANGO_SETTINGS_MODULE="config.settings"; Write-Host "✓ Environment ready - DJANGO_SETTINGS_MODULE: $env:DJANGO_SETTINGS_MODULE" -ForegroundColor Green; Write-Host "Checking drf_yasg format attributes..." -ForegroundColor Cyan; python manage.py shell -c "from drf_yasg import openapi; print('FORMAT_DECIMAL:', hasattr(openapi, 'FORMAT_DECIMAL')); print('FORMAT_PASSWORD:', hasattr(openapi, 'FORMAT_PASSWORD'))"
```

## Alternative: Use the Script

Run the provided PowerShell script:

```powershell
.\check_drf_yasg.ps1
```

## Step-by-Step (If You Prefer)

```powershell
# 1. Navigate to server directory (if not already there)
cd server

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Set Django settings module
$env:DJANGO_SETTINGS_MODULE="config.settings"

# 4. Verify environment
Write-Host "DJANGO_SETTINGS_MODULE: $env:DJANGO_SETTINGS_MODULE"

# 5. Run check via Django shell (this properly loads Django apps)
python manage.py shell -c "from drf_yasg import openapi; print('FORMAT_DECIMAL:', hasattr(openapi, 'FORMAT_DECIMAL')); print('FORMAT_PASSWORD:', hasattr(openapi, 'FORMAT_PASSWORD'))"
```

## Expected Output

```
✓ Environment ready - DJANGO_SETTINGS_MODULE: config.settings
Checking drf_yasg format attributes...
FORMAT_DECIMAL: True
FORMAT_PASSWORD: True
```

## Why This Works

- `python manage.py shell` properly initializes Django and loads all apps
- The `-c` flag allows running Python code directly in the shell
- This avoids the "Apps aren't loaded yet" error that occurs with `python -c`

## Notes

- **Settings Module**: `config.settings` (from `server/manage.py`)
- **Virtual Environment**: Automatically detected and activated if present
- **Django Shell**: Properly loads Django apps before running code

