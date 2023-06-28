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
v10.register(
    'meeting_results',
    views.MeetingResultViewSet,
    basename='meeting_results'
)

urlpatterns = [
    path('', include(v10.urls)),
]
