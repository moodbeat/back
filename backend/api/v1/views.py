import uuid

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from users.models import Department, Hobby, InviteCode, Position, User

from .serializers import (DepartmentSerializer, HobbySerializer,
                          PositionSerializer, RegisterSerializer,
                          SendInviteSerializer, UserSerializer)
from .utils import decode_data, encode_data, send_code


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('email', 'first_name', 'last_name',
                        'role', 'department', 'position')
    http_method_names = ('get', 'patch')

    def get_queryset(self):
        queryset = (
            User.objects
            .filter(is_active=True, is_superuser=False)
            .select_related('department', 'position')
            .prefetch_related('hobbies')
        )
        return queryset


class SendInviteView(APIView):
    '''Отправка на почту ссылки для регистрации'''

    @swagger_auto_schema(
        request_body=SendInviteSerializer,
        operation_id='users_send_invite'
    )
    def post(self, request):
        serializer = SendInviteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data.get('email')

        if User.objects.filter(email=email).exists():
            data = {'result': 'Пользователь с таким email уже зарегистрирован'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        elif InviteCode.objects.filter(email=email).exists():
            encoded_uuid = self.create_invite_code(email, retry=True)
            send_code(email=email, code=encoded_uuid, again=True)
            data = {'result': 'Ссылка отправлена повторно'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            encoded_uuid = self.create_invite_code(email)
            send_code(email=email, code=encoded_uuid)
            data = {'result': 'Ссылка для регистрации отправлена на email'}
            return Response(data, status=status.HTTP_200_OK)

    def create_invite_code(self, email: str, retry: bool = False) -> str:
        uuid_code = uuid.uuid4()
        encoded_uuid = encode_data(settings.INVITE_SECRET_KEY, str(uuid_code))
        if retry:
            InviteCode.objects.filter(email=email).update(code=uuid_code)
            return encoded_uuid
        InviteCode.objects.create(email=email, code=uuid_code)
        return encoded_uuid


class RegisterView(APIView):
    '''Регистрация по ссылке-приглашению'''

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        operation_id='users_register'
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        invite_code = serializer.validated_data.pop('invite_code')
        try:
            decode_uuid = decode_data(settings.INVITE_SECRET_KEY, invite_code)
            invite_code = InviteCode.objects.get(code=decode_uuid)
        except Exception:
            data = {'result': 'Недействительный ключ-приглашение'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        email = invite_code.email
        password = make_password(serializer.validated_data.pop('password'))
        User.objects.create(
            email=email, password=password, **serializer.validated_data
        )
        invite_code.delete()

        data = {'result': 'Пользователь успешно добавлен'}
        return Response(data, status=status.HTTP_201_CREATED)


class DepartmentViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'description')
    http_method_names = ('get', 'post', 'patch', 'delete')


class PositionViewSet(ModelViewSet):
    serializer_class = PositionSerializer
    queryset = Position.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'description')
    http_method_names = ('get', 'post', 'patch', 'delete')


class HobbyViewSet(ModelViewSet):
    serializer_class = HobbySerializer
    queryset = Hobby.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    http_method_names = ('get', 'post', 'patch', 'delete')
