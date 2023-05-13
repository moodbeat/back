from api.v1 import urls
from django.urls import include, path

urlpatterns = [
    path('v1/', include(urls)),
]
