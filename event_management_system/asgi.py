import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "event_management_system.settings.production")

application = get_asgi_application()
