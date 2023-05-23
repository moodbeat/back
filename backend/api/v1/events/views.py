from api.v1.permissions import (ChiefSafePermission, EmployeeSafePermission,
                                HRAllPermission)
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from events.models import Entry
from rest_framework.viewsets import ModelViewSet

from .filters import EntryFilter
from .serializers import EntryReadSerializer, EntryWriteSerializer

User = get_user_model()


class EntryViewSet(ModelViewSet):
    queryset = Entry.objects.select_related('category', 'author').all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EntryFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [
        HRAllPermission | ChiefSafePermission | EmployeeSafePermission
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EntryReadSerializer
        return EntryWriteSerializer
