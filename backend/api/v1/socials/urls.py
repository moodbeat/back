from django.urls import include, path, re_path

from api.v1.utils import OptionalSlashRouter

from . import views

v10 = OptionalSlashRouter()

v10.register('statuses', views.StatusViewSet, basename='statuses')
v10.register('likes', views.LikeViewSet, basename='likes')

urlpatterns = [
    path('', include(v10.urls)),
    re_path(
        r'^help_types/?$',
        views.HelpViewSet.as_view(),
        name='help_types'
    ),
    re_path(
        r'^specialists/?$',
        views.SpecialistsView.as_view(),
        name='specialists'
    ),
    re_path(
        r'^need_help/?$',
        views.NeedHelpView.as_view(),
        name='need_help'
    ),
]
