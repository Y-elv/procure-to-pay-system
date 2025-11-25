# Swagger UI Setup at /api-doc/ - Complete Guide

## Changes Applied

All changes have been applied to make Swagger UI available at `/api-doc/` with proper error handling.

## 1. URLs Configuration (`server/config/urls.py`)

**Added Swagger UI at `/api-doc/`:**

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/requests/', include('requests.urls')),
    # Swagger/OpenAPI documentation
    path('api-doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-alt'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/openapi/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
```

**Key Points:**
- `/api-doc/` - Main Swagger UI endpoint (new)
- `/swagger/` - Alternative endpoint (kept for compatibility)
- Uses `with_ui('swagger')` for classic Swagger UI
- `cache_timeout=0` for development (no caching)
- `permission_classes=(permissions.AllowAny,)` - Public access

## 2. ViewSet Fix (`server/requests/views.py`)

**Fixed `get_queryset()` to handle schema generation:**

```python
def get_queryset(self):
    """Filter queryset based on user role."""
    # Handle schema generation (Swagger UI) - avoid AnonymousUser errors
    if getattr(self, 'swagger_fake_view', False):
        return PurchaseRequest.objects.none()
    
    user = self.request.user
    
    if user.is_staff_role():
        # Staff sees only their own requests
        return PurchaseRequest.objects.filter(created_by=user)
    elif user.can_approve() or user.is_finance():
        # Approvers and finance see all requests
        return PurchaseRequest.objects.all()
    else:
        # Fallback
        return PurchaseRequest.objects.filter(created_by=user)
```

**Why This Fix:**
- When Swagger generates the schema, it creates a fake view instance
- The fake view has `swagger_fake_view=True` attribute
- Without this check, accessing `request.user` on AnonymousUser causes errors
- Returns empty queryset during schema generation (safe)

## 3. Settings Fix (`server/config/settings.py`)

**Fixed SWAGGER_SETTINGS:**

```python
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'example',
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.InlineSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
}
```

**Changes Made:**
- ✅ Removed invalid `'drf_yasg.inspectors.CamelCaseJSONRenderer'` (doesn't exist)
- ✅ Added `'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema'`
- ✅ Removed invalid `'DEFAULT_INFO': 'config.urls.schema_view'` (not needed)

## 4. Startup Message (`server/manage.py`)

**Added Swagger URL to startup message:**

```python
# Print startup messages
print(f"🚀 Django server is running on http://localhost:{app_port}")
print(f"📚 Swagger UI available at: http://127.0.0.1:{app_port}/api-doc/")
```

**Output when server starts:**
```
DB connected
🚀 Django server is running on http://localhost:8001
📚 Swagger UI available at: http://127.0.0.1:8001/api-doc/
```

## Testing the Setup

### Step 1: Start the Server

```powershell
cd server
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### Step 2: Verify Output

You should see:
```
DB connected
🚀 Django server is running on http://localhost:8001
📚 Swagger UI available at: http://127.0.0.1:8001/api-doc/
```

### Step 3: Access Swagger UI

Open your browser and navigate to:
- **Main URL**: `http://127.0.0.1:8001/api-doc/`
- **Alternative**: `http://127.0.0.1:8001/swagger/`

### Step 4: Test Interactive Features

1. Click "Authorize" button (top right)
2. Enter: `Bearer <your_jwt_token>`
3. Click "Authorize" and "Close"
4. Test endpoints directly from Swagger UI

## Troubleshooting

### Issue: "Apps aren't loaded yet" Error

**Solution:** The `swagger_fake_view` check in `get_queryset()` handles this. If you see this error elsewhere, add similar checks to other queryset methods.

### Issue: AnonymousUser Attribute Error

**Solution:** Already fixed in `PurchaseRequestViewSet.get_queryset()`. The check `if getattr(self, 'swagger_fake_view', False)` prevents accessing user attributes during schema generation.

### Issue: Swagger Page Not Loading

**Check:**
1. Server is running on correct port
2. URL is correct: `http://127.0.0.1:8001/api-doc/`
3. No errors in server console
4. `drf_yasg` is installed: `pip install drf-yasg`

### Issue: Endpoints Not Showing

**Check:**
1. All apps are in `INSTALLED_APPS` in `settings.py`
2. URLs are properly included in `config/urls.py`
3. ViewSets have proper `swagger_auto_schema` decorators

## Environment Variables

Ensure these are set (if using `.env`):

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

## Summary

✅ Swagger UI available at `/api-doc/`
✅ Fixed `get_queryset()` to handle schema generation
✅ Fixed `SWAGGER_SETTINGS` (removed invalid references)
✅ Added startup message with Swagger URL
✅ All endpoints should be visible and interactive

The Swagger UI is now fully functional and ready to use!

