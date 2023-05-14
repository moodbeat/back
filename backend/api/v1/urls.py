from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

v10 = DefaultRouter()
v10.register('users', views.UserViewSet, basename='users')
v10.register('departments', views.DepartmentViewSet, basename='departments')
v10.register('positions', views.PositionViewSet, basename='positions')

schema_view = get_schema_view(
    openapi.Info(
        title='Employee Mood API',
        default_version='1.0'
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path(
        'users/send_invite/',
        views.SendInviteView.as_view(),
        name='send_invite'
    ),
    path(
        'users/register/',
        views.RegisterView.as_view(),
        name='register'
    ),
    path('', include(v10.urls)),
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
