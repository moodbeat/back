from django.urls import include, path

from api.v1.metrics import views
from api.v1.utils import OptionalSlashRouter

v10 = OptionalSlashRouter()

v10.register('conditions', views.ConditionViewSet, basename='conditions')
v10.register('surveys', views.SurveyViewSet, basename='surveys')
v10.register('results', views.CompletedSurveyViewSet, basename='results')

urlpatterns = [
    path('', include(v10.urls)),
]
