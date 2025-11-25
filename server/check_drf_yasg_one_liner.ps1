# One-liner version - Copy and paste this entire block into PowerShell
if (Test-Path "venv\Scripts\Activate.ps1") { & .\venv\Scripts\Activate.ps1 }; $env:DJANGO_SETTINGS_MODULE="config.settings"; Write-Host "✓ Environment ready - DJANGO_SETTINGS_MODULE: $env:DJANGO_SETTINGS_MODULE" -ForegroundColor Green; Write-Host "Checking drf_yasg format attributes..." -ForegroundColor Cyan; python manage.py shell -c "from drf_yasg import openapi; print('FORMAT_DECIMAL:', hasattr(openapi, 'FORMAT_DECIMAL')); print('FORMAT_PASSWORD:', hasattr(openapi, 'FORMAT_PASSWORD'))"

