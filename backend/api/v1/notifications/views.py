from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.v1.notifications.filters import NotificationFilter
from api.v1.notifications.serializers import NotificationSerializer
from api.v1.permissions import NotificationUserOnly
from notifications.models import Notification


class NotificationViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NotificationFilter
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Notification.objects.select_related(
                'user'
            ).filter(user=self.request.user).all()
        return None

    def get_permissions(self):
        if self.action == 'viewed':
            self.permission_classes = (NotificationUserOnly,)
        return super().get_permissions()

    @action(
        methods=['get'], detail=True,
    )
    def viewed(self, request, pk):
        notification = self.get_object()
        notification.is_viewed = True
        notification.save()
        serializer = self.serializer_class(notification)
        return Response(serializer.data, status.HTTP_200_OK)
