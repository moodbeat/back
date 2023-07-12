from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.v1.events import urls as urls_events
from api.v1.metrics import urls as urls_metrics
from api.v1.notifications import urls as urls_notifications
from api.v1.services import urls as urls_services
from api.v1.socials import urls as urls_socials
from api.v1.users import urls as urls_users

schema_view = get_schema_view(
    openapi.Info(
        title='MoodBeat API',
        default_version='1.0'
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(urls_users)),
    path('', include(urls_notifications)),
    path('socials/', include(urls_socials)),
    path('metrics/', include(urls_metrics)),
    path('', include(urls_events)),
    path('services/', include(urls_services)),
    path('auth/', include('djoser.urls.jwt')),
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    )
]
