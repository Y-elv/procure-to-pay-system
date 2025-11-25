# Django Environment Setup for Windows PowerShell

## Quick Setup (One-Liner)

Copy and paste this command into your PowerShell terminal (from the `server` directory with your virtual environment activated):

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings"; Write-Host "✓ DJANGO_SETTINGS_MODULE set to: $env:DJANGO_SETTINGS_MODULE" -ForegroundColor Green; python -c "from drf_yasg import openapi; print('FORMAT_DECIMAL:', hasattr(openapi, 'FORMAT_DECIMAL')); print('FORMAT_PASSWORD:', hasattr(openapi, 'FORMAT_PASSWORD'))"
```

## Step-by-Step Instructions

### 1. Navigate to Server Directory

```powershell
cd server
```

### 2. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Set DJANGO_SETTINGS_MODULE

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings"
```

### 4. Verify the Environment Variable

```powershell
Write-Host "DJANGO_SETTINGS_MODULE is set to: $env:DJANGO_SETTINGS_MODULE"
```

### 5. Check drf_yasg Format Attributes

```powershell
python -c "from drf_yasg import openapi; print('FORMAT_DECIMAL:', hasattr(openapi, 'FORMAT_DECIMAL')); print('FORMAT_PASSWORD:', hasattr(openapi, 'FORMAT_PASSWORD'))"
```

## Expected Output

When you run the one-liner, you should see:

```
✓ DJANGO_SETTINGS_MODULE set to: config.settings
FORMAT_DECIMAL: True
FORMAT_PASSWORD: True
```

## Notes

- **Settings Module Path**: `config.settings` (detected from `server/manage.py`)
- **Project Structure**: `server/config/settings.py`
- **Environment Variable**: Set for current PowerShell session only
- **Persistence**: To make it permanent, add to your PowerShell profile or `.env` file

## Alternative: Using the Script

You can also use the provided PowerShell script:

```powershell
.\set_django_env.ps1
```

## Troubleshooting

If you get errors:

1. **Make sure you're in the `server` directory**
2. **Activate your virtual environment first**
3. **Ensure Django and drf_yasg are installed**: `pip install -r requirements.txt`

