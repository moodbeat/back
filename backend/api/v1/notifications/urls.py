from django.urls import include, path, re_path

from api.v1.notifications import views
from api.v1.notifications.consumers import UserNotifyConsumer
from api.v1.utils import OptionalSlashRouter

v10 = OptionalSlashRouter()

v10.register(
    'notifications', views.NotificationViewSet, basename='notifications'
)

urlpatterns = [
    path('', include(v10.urls)),
]

ws_urlpatterns = [
    re_path(
        r'^ws/notifications/?$',
        UserNotifyConsumer.as_asgi()
    ),
]
