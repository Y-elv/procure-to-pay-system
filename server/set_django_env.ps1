# PowerShell script to set DJANGO_SETTINGS_MODULE and verify drf_yasg format attributes
# Run this from the server directory with your virtual environment activated

Write-Host "Setting DJANGO_SETTINGS_MODULE..." -ForegroundColor Cyan
$env:DJANGO_SETTINGS_MODULE = "config.settings"
Write-Host "✓ DJANGO_SETTINGS_MODULE set to: $env:DJANGO_SETTINGS_MODULE" -ForegroundColor Green

Write-Host "`nChecking drf_yasg format attributes..." -ForegroundColor Cyan
python -c "from drf_yasg import openapi; print('FORMAT_DECIMAL:', hasattr(openapi, 'FORMAT_DECIMAL')); print('FORMAT_PASSWORD:', hasattr(openapi, 'FORMAT_PASSWORD'))"

Write-Host "`n✓ Environment check complete!" -ForegroundColor Green

