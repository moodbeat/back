from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r'^download-log/?$',
        views.DownloadLogView.as_view(),
        name='download_log'
    ),
]
