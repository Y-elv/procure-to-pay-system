#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
        
        # Handle runserver command with custom port
        if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
            # Get port from environment or default to 8001
            app_port_raw = os.getenv('APP_PORT', '8001')
            
            # Sanitize port: extract only the number (remove any ":" or host prefixes)
            app_port = app_port_raw.strip()
            if ':' in app_port:
                app_port = app_port.split(':')[-1]
            # Remove any non-numeric characters except digits
            app_port = ''.join(filter(str.isdigit, app_port))
            if not app_port:
                app_port = '8001'  # Fallback to 8001 if sanitization fails
            
            # If port is not specified in command, use APP_PORT
            if len(sys.argv) == 2:
                # No address/port specified, use APP_PORT (just the port number)
                sys.argv.append(app_port)
            elif len(sys.argv) == 3:
                # Check if port is specified in the argument
                if ':' in sys.argv[2]:
                    # Address:port format, extract port for message
                    app_port = sys.argv[2].split(':')[-1]
                elif sys.argv[2].isdigit():
                    # Just a port number, use it
                    app_port = sys.argv[2]
                else:
                    # Only address specified, append port
                    sys.argv[2] = f"{sys.argv[2]}:{app_port}"
            
            # Print startup messages
            print(f"🚀 Django server is running on http://localhost:{app_port}")
            print(f"📚 Swagger UI available at: http://127.0.0.1:{app_port}/api-doc/")
        
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

