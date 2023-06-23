from django.urls import include, path

from api.v1.utils import OptionalSlashRouter

from . import views

v10 = OptionalSlashRouter()

v10.register(
    'entries/categories',
    views.CategoryViewSet,
    basename='categories'
)
v10.register('entries', views.EntryViewSet, basename='entries')
v10.register('events', views.EventViewSet, basename='events')

urlpatterns = [
    path('', include(v10.urls)),
]
