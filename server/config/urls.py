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

schema_view = get_schema_view(
    openapi.Info(
        title="Procure-to-Pay API",
        default_version='v1',
        description="""
        # Procure-to-Pay System API Documentation
        
        Complete REST API for managing purchase requests, approvals, and receipts.
        
        ## Authentication
        Most endpoints require JWT authentication. Register or login to get your access token.
        
        ## User Roles
        - **staff**: Create and manage own purchase requests
        - **approver_level_1**: First-level approval authority
        - **approver_level_2**: Second-level approval authority  
        - **finance**: View all requests and validate receipts
        
        ## Base URL
        All API endpoints are prefixed with `/api/`
        
        ## Workflow
        1. Staff creates purchase request
        2. Level 1 Approver reviews and approves/rejects
        3. Level 2 Approver reviews and approves/rejects
        4. If both approve → Request is approved → PO generated
        5. Staff submits receipt
        6. Finance validates receipt against PO
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(
            name="API Support",
            email="contact@procuretopay.local",
            url="https://procuretopay.local"
        ),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/auth/', include('core.urls')),
        path('api/requests/', include('requests.urls')),
    ],
)

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

