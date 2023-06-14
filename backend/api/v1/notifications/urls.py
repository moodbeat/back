from django.urls import re_path

from .consumers import UserNotifyConsumer

ws_urlpatterns = [
    re_path(
        r'^ws/notifications/?$',
        UserNotifyConsumer.as_asgi()
    )
]
