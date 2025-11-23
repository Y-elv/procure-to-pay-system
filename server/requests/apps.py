from django.apps import AppConfig


class RequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'requests'
    
    def ready(self):
        """Import signals when app is ready."""
        import requests.signals  # noqa

