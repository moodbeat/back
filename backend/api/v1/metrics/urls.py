from api.v1.utils import OptionalSlashRouter
from django.urls import include, path

from . import views


v10 = OptionalSlashRouter()

v10.register('conditions', views.ConditionViewSet, basename='conditions')
# v10.register('surveys', views.SurveyViewSet, basename='surveys')

urlpatterns = [
    path('', include(v10.urls)),
]