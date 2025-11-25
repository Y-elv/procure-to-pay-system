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
import os

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

# Get production domain from environment or use default
PRODUCTION_DOMAIN = os.getenv('PRODUCTION_DOMAIN', 'my-production-domain.com')
HTTP_PORT = os.getenv('HTTP_PORT', '8000')

# Custom view to ensure servers are in OpenAPI JSON
def schema_json_with_servers(request):
    """Return OpenAPI schema with servers configured for HTTP and HTTPS schemes."""
    response = schema_view.without_ui(cache_timeout=0)(request)
    if response.status_code == 200:
        try:
            schema = json.loads(response.content)
            # Remove any git-related text from description
            if 'info' in schema and 'description' in schema['info']:
                description = schema['info']['description']
                # Remove git push commands
                description = description.replace('git push --set-upstream origin fix-swagger-Ui', '')
                description = description.replace('git push --set-upstream origin fix-swagger-ui', '')
                description = description.replace('fix-swagger-Ui', '')
                description = description.replace('fix-swagger-ui', '')
                schema['info']['description'] = description.strip()
            
            # Configure servers for HTTP and HTTPS schemes
            # HTTP uses localhost, HTTPS uses production domain
            schema['servers'] = [
                {
                    "url": f"http://localhost:{HTTP_PORT}",
                    "description": "HTTP - Development server (localhost)"
                },
                {
                    "url": f"https://{PRODUCTION_DOMAIN}",
                    "description": "HTTPS - Production server"
                }
            ]
            
            # Add schemes to support HTTP and HTTPS dropdown
            schema['schemes'] = ['http', 'https']
            
            return JsonResponse(schema, json_dumps_params={'indent': 2})
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
    return response

# Custom Swagger UI view that removes git text and ensures servers/authorize are visible
def swagger_ui_clean(request):
    """Swagger UI with git text removed and servers/authorize visible."""
    from django.http import HttpResponse
    
    # Get the base Swagger UI response
    base_response = schema_view.with_ui('swagger', cache_timeout=0)(request)
    
    # Render the response if it's a TemplateResponse
    if hasattr(base_response, 'render'):
        base_response = base_response.render()
    
    if hasattr(base_response, 'content'):
        # Inject configuration and CSS/JavaScript to customize Swagger UI
        config_script = f"""
        <script>
            // Swagger UI configuration
            window.SWAGGER_CONFIG = {{
                HTTP_PORT: '{HTTP_PORT}',
                PRODUCTION_DOMAIN: '{PRODUCTION_DOMAIN}'
            }};
        </script>
        """
        clean_script = """
        <style>
            /* Hide base URL display and all URL links at the top */
            .swagger-ui .info .base-url,
            .swagger-ui .info .title small pre,
            .swagger-ui .info .title small,
            .swagger-ui .info .base-url pre,
            .swagger-ui .info .base-url code,
            .swagger-ui .info .base-url a,
            .swagger-ui .info .title small code,
            .swagger-ui .info .title small a {
                display: none !important;
                visibility: hidden !important;
            }
            .swagger-ui .info .title {
                margin-bottom: 0 !important;
            }
            
            /* Hide format=openapi links and URLs in header/topbar */
            a[href*="format=openapi"],
            a[href*="api-doc"],
            a[href*="api/openapi"],
            .swagger-ui .topbar a[href*="format"],
            .swagger-ui .topbar a[href*="api-doc"],
            .swagger-ui .info a[href*="format"],
            .swagger-ui .info a[href*="api-doc"] {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* Hide format=openapi from search inputs and any input showing URLs */
            input[type="text"][placeholder*="format"],
            input[type="search"][value*="format=openapi"],
            input[value*="api-doc"],
            input[value*="format=openapi"] {
                display: none !important;
            }
            
            /* Hide any elements containing the api-doc URL */
            *:contains("http://127.0.0.1:8001/api-doc/"),
            *:contains("http://127.0.0.1:8001/api-doc/?format=openapi"),
            *:contains("api-doc/?format=openapi") {
                display: none !important;
            }
            
            /* Hide URL displays in info section */
            .swagger-ui .info .url,
            .swagger-ui .info .base-url-container,
            .swagger-ui .info .scheme-container + * {
                display: none !important;
            }
        </style>
        <script>
            window.addEventListener('load', function() {
                // Remove any git-related text from the page
                function removeGitText() {
                    var allText = document.body.innerText || document.body.textContent || '';
                    if (allText.includes('git push') || allText.includes('fix-swagger')) {
                        var walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        var node;
                        while (node = walker.nextNode()) {
                            if (node.textContent.includes('git push') || 
                                node.textContent.includes('fix-swagger')) {
                                node.textContent = node.textContent
                                    .replace(/git push[^\\n]*/g, '')
                                    .replace(/fix-swagger[^\\s]*/g, '')
                                    .trim();
                            }
                        }
                    }
                }
                
                // Remove all URL displays at the top
                function removeTopUrls() {
                    // Remove base URL text and links
                    var walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
                        null,
                        false
                    );
                    var node;
                    var nodesToRemove = [];
                    
                    while (node = walker.nextNode()) {
                        var text = node.textContent || '';
                        var href = node.href || (node.parentElement && node.parentElement.href) || '';
                        
                        // Check for URL patterns
                        if (text.includes('http://127.0.0.1:8001/api-doc/') ||
                            text.includes('api-doc/?format=openapi') ||
                            text.includes('Base URL:') ||
                            text.includes('127.0.0.1:8001/api') ||
                            href.includes('format=openapi') ||
                            href.includes('api-doc')) {
                            
                            // If it's a text node, remove the text
                            if (node.nodeType === Node.TEXT_NODE) {
                                var parent = node.parentElement;
                                if (parent && (parent.tagName === 'A' || parent.tagName === 'CODE' || parent.tagName === 'PRE')) {
                                    parent.style.display = 'none';
                                } else {
                                    node.textContent = node.textContent
                                        .replace(/http:\\/\\/127\\.0\\.0\\.1:8001\\/api-doc\\/[^\\s]*/g, '')
                                        .replace(/api-doc\\/?[^\\s]*format=openapi[^\\s]*/g, '')
                                        .replace(/Base URL:[^\\n]*/gi, '')
                                        .replace(/127\\.0\\.0\\.1:8001\\/api/g, '')
                                        .trim();
                                }
                            }
                            // If it's an element (link), hide it
                            else if (node.nodeType === Node.ELEMENT_NODE) {
                                if (node.tagName === 'A' || node.tagName === 'CODE' || node.tagName === 'PRE') {
                                    node.style.display = 'none';
                                    node.style.visibility = 'hidden';
                                }
                            }
                        }
                    }
                    
                    // Remove all links containing api-doc or format=openapi
                    var links = document.querySelectorAll('a[href*="api-doc"], a[href*="format=openapi"]');
                    links.forEach(function(link) {
                        link.style.display = 'none';
                        link.style.visibility = 'hidden';
                        if (link.parentElement) {
                            link.parentElement.style.display = 'none';
                        }
                    });
                    
                    // Remove any code/pre elements showing URLs
                    var codeElements = document.querySelectorAll('code, pre');
                    codeElements.forEach(function(el) {
                        var text = el.textContent || '';
                        if (text.includes('api-doc') || text.includes('format=openapi') || 
                            text.includes('127.0.0.1:8001/api-doc')) {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                        }
                    });
                }
                
                // Remove format=openapi from search inputs
                function removeFormatFromSearch() {
                    var inputs = document.querySelectorAll('input[type="text"], input[type="search"], input');
                    inputs.forEach(function(input) {
                        if (input.value && (input.value.includes('format=openapi') || input.value.includes('api-doc'))) {
                            input.value = input.value.replace(/[?&]format=openapi/g, '').replace(/api-doc[^\\s]*/g, '');
                        }
                        if (input.placeholder && (input.placeholder.includes('format=openapi') || input.placeholder.includes('api-doc'))) {
                            input.placeholder = input.placeholder.replace(/[?&]format=openapi/g, '').replace(/api-doc[^\\s]*/g, '');
                        }
                    });
                }
                
                // Run immediately and after delays
                removeGitText();
                removeTopUrls();
                removeFormatFromSearch();
                
                setTimeout(function() {
                    removeGitText();
                    removeTopUrls();
                    removeFormatFromSearch();
                }, 100);
                
                setTimeout(function() {
                    removeGitText();
                    removeTopUrls();
                    removeFormatFromSearch();
                }, 500);
                
                setTimeout(function() {
                    removeTopUrls();
                    removeFormatFromSearch();
                }, 1000);
                
                // Configure HTTP and HTTPS schemes with proper server URLs
                function configureSchemes() {
                    if (window.ui && window.ui.spec) {
                        var spec = window.ui.spec;
                        // Get configuration values
                        var httpPort = (window.SWAGGER_CONFIG && window.SWAGGER_CONFIG.HTTP_PORT) || '8000';
                        var productionDomain = (window.SWAGGER_CONFIG && window.SWAGGER_CONFIG.PRODUCTION_DOMAIN) || 'my-production-domain.com';
                        
                        // Set servers: HTTP uses localhost, HTTPS uses production domain
                        spec.servers = [
                            {
                                url: 'http://localhost:' + httpPort,
                                description: 'HTTP - Development server (localhost)'
                            },
                            {
                                url: 'https://' + productionDomain,
                                description: 'HTTPS - Production server'
                            }
                        ];
                        
                        // Ensure schemes are set for HTTP/HTTPS dropdown
                        spec.schemes = ['http', 'https'];
                        
                        // Update the spec
                        window.ui.specActions.updateSpec(JSON.stringify(spec));
                        
                        // Ensure scheme selector is visible and functional
                        var schemeContainer = document.querySelector('.scheme-container');
                        if (schemeContainer) {
                            schemeContainer.style.display = 'block';
                            
                            // Find or create scheme selector
                            var schemeSelect = schemeContainer.querySelector('select');
                            if (!schemeSelect) {
                                // Create scheme selector if it doesn't exist
                                schemeSelect = document.createElement('select');
                                schemeSelect.className = 'scheme-selector';
                                schemeContainer.appendChild(schemeSelect);
                            }
                            
                            // Ensure both http and https options exist
                            var hasHttp = false;
                            var hasHttps = false;
                            Array.from(schemeSelect.options).forEach(function(option) {
                                if (option.value === 'http' || option.value.toLowerCase() === 'http') hasHttp = true;
                                if (option.value === 'https' || option.value.toLowerCase() === 'https') hasHttps = true;
                            });
                            
                            if (!hasHttp) {
                                var httpOption = document.createElement('option');
                                httpOption.value = 'http';
                                httpOption.textContent = 'http';
                                schemeSelect.appendChild(httpOption);
                            }
                            
                            if (!hasHttps) {
                                var httpsOption = document.createElement('option');
                                httpsOption.value = 'https';
                                httpsOption.textContent = 'https';
                                schemeSelect.appendChild(httpsOption);
                            }
                            
                            // Add change listener to update server URL based on selected scheme
                            schemeSelect.addEventListener('change', function() {
                                var selectedScheme = this.value;
                                if (spec.servers && spec.servers.length > 0) {
                                    if (selectedScheme === 'http') {
                                        // Switch to HTTP server (localhost)
                                        spec.servers[0].url = 'http://localhost:' + httpPort;
                                        if (spec.servers.length > 1) {
                                            spec.servers[1].url = 'http://localhost:' + httpPort;
                                        }
                                    } else if (selectedScheme === 'https') {
                                        // Switch to HTTPS server (production)
                                        spec.servers[0].url = 'https://' + productionDomain;
                                        if (spec.servers.length > 1) {
                                            spec.servers[1].url = 'https://' + productionDomain;
                                        }
                                    }
                                    window.ui.specActions.updateSpec(JSON.stringify(spec));
                                }
                            });
                        }
                    }
                }
                
                // Run configuration with delays to ensure UI is ready
                setTimeout(configureSchemes, 1500);
                setTimeout(configureSchemes, 2000);
                setTimeout(configureSchemes, 3000);
                
                // Ensure servers section is visible
                var serversSection = document.querySelector('.scheme-container');
                if (serversSection) {
                    serversSection.style.display = 'block';
                }
                
                // Ensure authorize button is visible
                var authorizeBtn = document.querySelector('.btn.authorize');
                if (authorizeBtn) {
                    authorizeBtn.style.display = 'inline-block';
                }
                
                // Continuously monitor and remove URLs and format=openapi
                setInterval(function() {
                    removeTopUrls();
                    removeFormatFromSearch();
                }, 1000);
            });
        </script>
        """
        try:
            content = base_response.content.decode('utf-8')
            # Remove git text from HTML content
            content = content.replace('git push --set-upstream origin fix-swagger-Ui', '')
            content = content.replace('git push --set-upstream origin fix-swagger-ui', '')
            content = content.replace('fix-swagger-Ui', '')
            content = content.replace('fix-swagger-ui', '')
            # Inject configuration and customization scripts
            content = content.replace('</head>', config_script + clean_script + '</head>')
            return HttpResponse(content, content_type='text/html')
        except (UnicodeDecodeError, AttributeError):
            pass
    
    return base_response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/requests/', include('requests.urls')),
    # Swagger/OpenAPI documentation
    path('api-doc/', swagger_ui_clean, name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-alt'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/openapi/', schema_json_with_servers, name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

