from django.conf import settings
from django.urls import re_path

from . import views

urlpatterns = []

if settings.DEV_SERVICES:
    urlpatterns += (
        re_path(
            r'^download-log/?$',
            views.DownloadLogView.as_view(),
            name='download_log'
        ),
    )
