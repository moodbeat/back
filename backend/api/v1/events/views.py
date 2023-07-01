from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.v1.permissions import (AllowAuthorOrReadOnly, ChiefPostPermission,
                                ChiefSafePermission, EmployeeSafePermission,
                                HRAllPermission)
from events.models import Category, Entry, Event, MeetingResult

from .filters import EntryFilter, EventFilter
from .serializers import (CategorySerializer, EntryReadSerializer,
                          EntryWriteSerializer, EventReadSerializer,
                          EventWriteSerializer, MeetingResultReadSerializer,
                          MeetingResultWriteSerializer)

User = get_user_model()


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer
    pagination_class = None


@method_decorator(name='create', decorator=swagger_auto_schema(
    responses={status.HTTP_201_CREATED: EntryWriteSerializer},
))
class EntryViewSet(ModelViewSet):
    # TODO оптимизировать запрос с prefetch на лайки рейквест юзера
    queryset = (
        Entry.objects
        .select_related('author')
        .prefetch_related('category', 'likes')
        .all()
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EntryFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [
        IsAuthenticated & AllowAuthorOrReadOnly & HRAllPermission
        | ChiefSafePermission | EmployeeSafePermission
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EntryReadSerializer
        return EntryWriteSerializer


class EventViewSet(ModelViewSet):
    # TODO оптимизировать запрос с prefetch на лайки рейквест юзера
    queryset = (
        Event.objects
        .select_related('author')
        .prefetch_related('likes')
        .all()
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [
        IsAuthenticated & AllowAuthorOrReadOnly & HRAllPermission
        | ChiefPostPermission | EmployeeSafePermission
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventReadSerializer
        return EventWriteSerializer


class MeetingResultViewSet(ModelViewSet):
    queryset = MeetingResult.objects.select_related(
        'organizer', 'employee', 'mental_state'
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('organizer', 'employee', 'mental_state')
    http_method_names = ('get', 'post',)
    permission_classes = (HRAllPermission,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MeetingResultReadSerializer
        return MeetingResultWriteSerializer
