from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """Run when Django starts."""
        try:
            from django.db import connection
            connection.ensure_connection()
            print("DB connected")
        except Exception:
            # Connection error will be shown by Django
            pass

