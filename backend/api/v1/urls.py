from api.v1.events import urls as urls_events
from api.v1.socials import urls as urls_socials
from api.v1.users import urls as urls_users
from api.v1.metrics import urls as urls_metrics
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title='Employee Mood API',
        default_version='1.0'
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(urls_users)),
    path('socials/', include(urls_socials)),
    path('', include(urls_events)),
    path('', include(urls_metrics)),
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
