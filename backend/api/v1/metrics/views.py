from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import request
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.viewsets import ModelViewSet
from api.v1.permissions import (ChiefSafePermission, EmployeeSafePermission,
                                HRAllPermission)
from metrics.models import Condition, Survey
from api.v1.metrics.serializers import ConditionReadSerializer, \
    ConditionWriteSerializer

User = get_user_model()


class ConditionViewSet(ModelViewSet):
    queryset = Condition.objects.all()
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ('get', 'post',)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConditionReadSerializer
        return ConditionWriteSerializer
