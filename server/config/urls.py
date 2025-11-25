"""
URL configuration for procure-to-pay system.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.http import JsonResponse
import json

# Create schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Procure-to-Pay API",
        default_version='v1',
        description="API documentation for Procure-to-Pay system",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/auth/', include('core.urls')),
        path('api/requests/', include('requests.urls')),
    ],
)

# Custom view to remove servers from OpenAPI JSON
def schema_json_no_servers(request):
    """Return OpenAPI schema without servers to hide base URL."""
    response = schema_view.without_ui(cache_timeout=0)(request)
    if response.status_code == 200:
        try:
            schema = json.loads(response.content)
            # Remove servers to hide base URL display
            schema.pop('servers', None)
            return JsonResponse(schema, json_dumps_params={'indent': 2})
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
    return response

# Custom Swagger UI view that hides base URL/server selector
def swagger_ui_no_base_url(request):
    """Swagger UI with hidden base URL/server selector."""
    from django.http import HttpResponse
    
    # Get the base Swagger UI response
    base_response = schema_view.with_ui('swagger', cache_timeout=0)(request)
    
    # Render the response if it's a TemplateResponse
    if hasattr(base_response, 'render'):
        base_response = base_response.render()
    
    if hasattr(base_response, 'content'):
        # Inject CSS and JavaScript to hide server selector and base URL
        hide_script = """
        <style>
            .swagger-ui .scheme-container,
            .swagger-ui .info .base-url,
            .swagger-ui .scheme-container .schemes,
            .swagger-ui .info .title small pre,
            .swagger-ui .info .title small {
                display: none !important;
            }
            .swagger-ui .info .title {
                margin-bottom: 0 !important;
            }
        </style>
        <script>
            window.addEventListener('load', function() {
                // Hide server selector
                var serverContainer = document.querySelector('.scheme-container');
                if (serverContainer) serverContainer.style.display = 'none';
                // Hide base URL in info section
                var baseUrl = document.querySelector('.info .base-url');
                if (baseUrl) baseUrl.style.display = 'none';
            });
        </script>
        """
        try:
            content = base_response.content.decode('utf-8')
            content = content.replace('</head>', hide_script + '</head>')
            return HttpResponse(content, content_type='text/html')
        except (UnicodeDecodeError, AttributeError):
            pass
    
    return base_response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/requests/', include('requests.urls')),
    # Swagger/OpenAPI documentation
    path('api-doc/', swagger_ui_no_base_url, name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-alt'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/openapi/', schema_json_no_servers, name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

