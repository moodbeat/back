from django.urls import re_path

from . import views

urlpatterns = [
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
]
