# PowerShell script to check drf_yasg format attributes using Django shell
# This avoids "Apps aren't loaded yet" error

Write-Host "`n=== Django drf_yasg Format Attributes Check ===" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment not found at venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "Continuing with current Python environment..." -ForegroundColor Yellow
}

# Set Django settings module
Write-Host "Setting DJANGO_SETTINGS_MODULE..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "config.settings"
Write-Host "✓ DJANGO_SETTINGS_MODULE set to: $env:DJANGO_SETTINGS_MODULE" -ForegroundColor Green

Write-Host ""
Write-Host "Checking drf_yasg format attributes via Django shell..." -ForegroundColor Cyan
Write-Host ""

# Use Django shell to run the check (this properly loads Django apps)
python manage.py shell -c "from drf_yasg import openapi; print('FORMAT_DECIMAL:', hasattr(openapi, 'FORMAT_DECIMAL')); print('FORMAT_PASSWORD:', hasattr(openapi, 'FORMAT_PASSWORD'))"

Write-Host ""
Write-Host "✓ Check complete!" -ForegroundColor Green

