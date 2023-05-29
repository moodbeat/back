import os

from django.core.asgi import get_asgi_application

# https://stackoverflow.com/questions/53683806/
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django_asgi_app = get_asgi_application()

from api.v1.users.urls import ws_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter(
    {
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(ws_urlpatterns)),
        )
    }
)
