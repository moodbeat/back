from django.urls import include, path, re_path

from api.v1.metrics import views
from api.v1.utils import OptionalSlashRouter

v10 = OptionalSlashRouter()

v10.register('conditions', views.ConditionViewSet, basename='conditions')
v10.register('life_balance', views.LifeBalanceViewSet, basename='life_balance')
v10.register(
    'surveys/results',
    views.CompletedSurveyViewSet,
    basename='surveys_results'
)
v10.register('surveys', views.SurveyViewSet, basename='surveys')
v10.register('burnouts', views.BurnoutViewSet, basename='burnouts')
v10.register('activities', views.ActivityViewSet, basename='activities')

urlpatterns = [
    re_path(
        r'^activities/average/?$',
        views.ActivityAveragePercentageListView.as_view(),
        name='activities_average'
    ),
    re_path(
        r'^life_directions/?$',
        views.LifeDirectionListView.as_view(),
        name='life_directions'
    ),
    re_path(
        r'^mental_states/?$',
        views.MentalStateViewSet.as_view(),
        name='mental_states'
    ),
    re_path(
        r'^activity_types/?$',
        views.ActivityTypeListView.as_view(),
        name='activity_types'
    ),
    path('', include(v10.urls)),
]
