import uuid

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from users.models import Department, Hobby, InviteCode, Position, User

from .permissions import (AllReadOnlyPermissions, ChiefPostPermission,
                          ChiefSafePermission, EmployeePostPermission,
                          EmployeeSafePermission, HRAllPermission)
from .serializers import (DepartmentSerializer, HobbySerializer,
                          PositionSerializer, RegisterSerializer,
                          SendInviteSerializer, UserSelfUpdateSerializer,
                          UserSerializer, UserUpdateSerializer,
                          VerifyInviteSerializer)
from .utils import decode_data, encode_data, send_code


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('email', 'first_name', 'last_name')
    filterset_fields = ('email', 'first_name', 'last_name', 'role', 'position')
    http_method_names = ('get', 'patch')
    permission_classes = [HRAllPermission | ChiefSafePermission]

    def get_queryset(self):
        queryset = (
            User.objects
            .filter(is_active=True, is_superuser=False)
            .select_related('position', 'position__department')
            .prefetch_related('hobbies')
        )
        return queryset

    @swagger_auto_schema(request_body=UserUpdateSerializer)
    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = UserUpdateSerializer
        return super().partial_update(request, *args, **kwargs)


class CurrentUserView(APIView):
    '''Данные текущего пользователя'''

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(responses={status.HTTP_200_OK: UserSerializer})
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserSelfUpdateSerializer)
    def patch(self, request):
        serializer = UserSelfUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendInviteView(APIView):
    '''Отправка на почту ссылки для регистрации'''

    permission_classes = (HRAllPermission,)

    @swagger_auto_schema(
        request_body=SendInviteSerializer,
        operation_id='users_send_invite',
        responses={
            status.HTTP_200_OK: 'Ссылка для регистрации отправлена на email',
            status.HTTP_400_BAD_REQUEST:
                ('Некорректный запрос. Ошибка валидации данных '
                 'или пользователь уже зарегистрирован')
        }
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
            data = {'result': 'Ссылка отправлена повторно',
                    'invite_code': encoded_uuid}  # пока оставлю агрыавлыьалвва
            return Response(data, status=status.HTTP_200_OK)
        else:
            encoded_uuid = self.create_invite_code(email)
            send_code(email=email, code=encoded_uuid)
            data = {'result': 'Ссылка для регистрации отправлена на email',
                    'invite_code': encoded_uuid}  # пока оставлю агрыавлыьалвва
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

    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        operation_id='users_register',
        responses={
            status.HTTP_200_OK: 'Пользователь успешно добавлен',
            status.HTTP_400_BAD_REQUEST: 'Недействительный ключ-приглашение'
        }
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


class VerifyInviteView(APIView):
    '''Проверка ключа-приглашения'''

    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=VerifyInviteSerializer,
        operation_id='users_verify_invite',
        responses={
            status.HTTP_200_OK: 'Ключ-приглашение прошел проверку',
            status.HTTP_400_BAD_REQUEST: 'Недействительный ключ-приглашение'
        }
    )
    def post(self, request):
        serializer = VerifyInviteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        invite_code = serializer.validated_data.get('invite_code')

        try:
            decode_data(settings.INVITE_SECRET_KEY, invite_code)
        except Exception:
            data = {'result': 'Недействительный ключ-приглашение'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data = {'result': 'Ключ-приглашение прошел проверку'}
        return Response(data, status=status.HTTP_200_OK)


class DepartmentViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = ('id', 'name',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [HRAllPermission | AllReadOnlyPermissions]


class PositionViewSet(ModelViewSet):
    serializer_class = PositionSerializer
    queryset = Position.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('id', 'name', 'department',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [
        HRAllPermission | ChiefSafePermission | EmployeeSafePermission
        | AllReadOnlyPermissions
    ]


class HobbyViewSet(ModelViewSet):
    serializer_class = HobbySerializer
    queryset = Hobby.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('id', 'name',)
    search_fields = ('name',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [
        HRAllPermission | ChiefSafePermission | ChiefPostPermission
        | EmployeeSafePermission | EmployeePostPermission
    ]
