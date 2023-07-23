import random
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.permissions import (AllReadOnlyPermissions, ChiefSafePermission,
                                HRAllPermission)
from spare_kits import invite_service
from users.documents import HobbyDocument
from users.models import (Department, Hobby, InviteCode, PasswordResetCode,
                          Position, TelegramCode, TelegramUser)

from .filters import (DepartmentInviteCodeFilter, ElasticSearchFilter,
                      PositionInviteCodeFilter)
from .serializers import (DepartmentSerializer, HobbySerializer,
                          PasswordChangeSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetSerializer, PositionSerializer,
                          RegisterSerializer, SendInviteSerializer,
                          TelegramTokenSerializer, UserSelfUpdateSerializer,
                          UserSerializer, UserUpdateSerializer,
                          VerifyInviteSerializer)

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('email', 'first_name', 'last_name')
    filterset_fields = ('email', 'first_name', 'last_name',
                        'role', 'department', 'position')
    http_method_names = ('get', 'patch')
    permission_classes = [HRAllPermission | ChiefSafePermission]

    def get_queryset(self):
        return (
            User.objects
            .filter(is_active=True, is_superuser=False)
            .select_related('position', 'department', 'mental_state')
            .prefetch_related('condition_set', 'hobbies')
        )

    @swagger_auto_schema(request_body=UserUpdateSerializer)
    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = UserUpdateSerializer
        return super().partial_update(request, *args, **kwargs)


class CurrentUserView(APIView):
    """Данные текущего пользователя."""

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserViewSet.get_queryset(self)

    @swagger_auto_schema(responses={status.HTTP_200_OK: UserSerializer})
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserSelfUpdateSerializer,
        manual_parameters=[
            openapi.Parameter(
                'delete_avatar',
                openapi.IN_QUERY,
                description='Параметр удаления аватара.',
                type=openapi.TYPE_BOOLEAN
            ),
        ]
    )
    def patch(self, request):
        serializer = UserSelfUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        delete_avatar = request.query_params.get('delete_avatar', None)
        user = self.request.user
        if delete_avatar:
            if user.avatar_full:
                user.avatar_full.delete(save=True)
            if serializer.initial_data.get('avatar', None):
                del serializer.initial_data['avatar']
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendInviteView(APIView):
    """Отправка на почту ссылки для регистрации."""

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

        if User.objects.filter(email__iexact=email).exists():
            data = {'detail': 'Пользователь с таким email уже зарегистрирован'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if InviteCode.objects.filter(email__iexact=email).exists():
            encoded_uuid = self.create_invite_code(email, retry=True)
            invite_service.send_invite_code(
                email=email, code=encoded_uuid, again=True
            )
            data = {'detail': 'Ссылка отправлена повторно',
                    'invite_code': encoded_uuid}  # пока оставлю агрыавлыьалвва
            return Response(data, status=status.HTTP_200_OK)

        encoded_uuid = self.create_invite_code(email)
        invite_service.send_invite_code(email=email, code=encoded_uuid)
        data = {'detail': 'Ссылка для регистрации отправлена на email',
                'invite_code': encoded_uuid}  # пока оставлю агрыавлыьалвва
        return Response(data, status=status.HTTP_200_OK)

    def create_invite_code(self, email: str, retry: bool = False) -> str:
        uuid_code = uuid.uuid4()
        encoded_uuid = invite_service.encode_data(
            settings.RESET_INVITE_SECRET_KEY, str(uuid_code)
        )
        user = self.request.user
        if retry:
            InviteCode.objects.filter(
                email__iexact=email, sender=user
            ).update(code=uuid_code)
            return encoded_uuid
        InviteCode.objects.create(email=email, sender=user, code=uuid_code)
        return encoded_uuid


class RegisterView(APIView):
    """Регистрация по ссылке-приглашению."""

    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        operation_id='users_register',
        responses={
            status.HTTP_201_CREATED: 'Пользователь успешно добавлен',
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
        decode_uuid = invite_service.verify_code(
            settings.RESET_INVITE_SECRET_KEY, invite_code, InviteCode
        )
        invite_code = InviteCode.objects.get(code=decode_uuid)

        email = invite_code.email
        password = make_password(serializer.validated_data.pop('password'))
        User.objects.create(
            email=email, password=password, **serializer.validated_data
        )
        invite_code.delete()

        data = {
            'detail': 'Пользователь успешно добавлен',
            'email': email,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class VerifyInviteView(APIView):
    """Проверка ключа-приглашения."""

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
        invite_service.verify_code(
            settings.RESET_INVITE_SECRET_KEY, invite_code, InviteCode
        )
        data = {'detail': 'Ключ-приглашение прошел проверку'}
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    """Отправка на почту ссылки на смену пароля."""

    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        operation_id='users_password_reset',
        responses={
            status.HTTP_200_OK: 'Ссылка на смену пароля отправлена на email',
            status.HTTP_400_BAD_REQUEST:
                ('Некорректный запрос. Ошибка валидации данных '
                 'или пользователь с таким email отсутствует')
        }
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data.get('email')

        if PasswordResetCode.objects.filter(email__iexact=email).exists():
            encoded_uuid = self.create_reset_code(email, retry=True)
            invite_service.send_reset_code(
                email=email, code=encoded_uuid, again=True
            )
            data = {'detail': 'Ссылка отправлена повторно',
                    'reset_code': encoded_uuid}  # тоже пока оставлю
            return Response(data, status=status.HTTP_200_OK)

        encoded_uuid = self.create_reset_code(email)
        invite_service.send_reset_code(email=email, code=encoded_uuid)
        data = {'detail': 'Ссылка на смену пароля отправлена на email',
                'reset_code': encoded_uuid}  # тоже пока оставлю
        return Response(data, status=status.HTTP_200_OK)

    def create_reset_code(self, email: str, retry: bool = False) -> str:
        uuid_code = uuid.uuid4()
        encoded_uuid = invite_service.encode_data(
            settings.RESET_INVITE_SECRET_KEY, str(uuid_code))
        if retry:
            PasswordResetCode.objects.filter(
                email__iexact=email
            ).update(code=uuid_code)
            return encoded_uuid
        PasswordResetCode.objects.create(email=email, code=uuid_code)
        return encoded_uuid


class PasswordResetConfirmView(APIView):
    """Новый пароль."""

    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        operation_id='users_password_reset_confirm',
        responses={
            status.HTTP_200_OK: 'Пароль успешно изменен.',
            status.HTTP_400_BAD_REQUEST: 'Недействительный ключ.'
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        reset_code = serializer.validated_data.pop('reset_code')
        decode_uuid = invite_service.verify_code(
            settings.RESET_INVITE_SECRET_KEY, reset_code, PasswordResetCode
        )
        reset_code = PasswordResetCode.objects.get(code=decode_uuid)

        email = reset_code.email
        password = make_password(serializer.validated_data.pop('password'))
        User.objects.filter(email__iexact=email).update(password=password)
        reset_code.delete()

        data = {'detail': 'Пароль успешно изменен.'}
        return Response(data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    """Смена пароля."""

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=PasswordChangeSerializer,
        operation_id='users_password_change',
        responses={
            status.HTTP_200_OK: 'Пароль успешно изменен.'
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        user = self.request.user
        current_password = serializer.validated_data.get('current_password')

        if not user.check_password(current_password):
            data = {'detail': 'Текущий пароль указан неверно.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        password = serializer.validated_data.get('new_password')
        user.set_password(password)
        user.save()
        data = {'detail': 'Пароль успешно изменен.'}
        return Response(data, status=status.HTTP_200_OK)


class TelegramSendCodeView(APIView):
    """Отправка на почту кода для авторизации в боте."""

    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        operation_id='users_telegram_send_code',
        responses={
            status.HTTP_200_OK:
                'Код для авторизации в боте отправлен на email',
            status.HTTP_400_BAD_REQUEST:
                ('Некорректный запрос. Ошибка валидации данных '
                 'или пользователь с таким email отсутствует')
        }
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data.get('email')

        if TelegramCode.objects.filter(email__iexact=email).exists():
            telegram_code = self.create_telegram_code(email, retry=True)
            invite_service.send_telegram_code(
                email=email, code=telegram_code, again=True
            )
            data = {'detail': 'Код отправлен повторно',
                    'telegram_code': telegram_code}
            return Response(data, status=status.HTTP_200_OK)

        telegram_code = self.create_telegram_code(email)
        invite_service.send_telegram_code(email=email, code=telegram_code)
        data = {'detail': 'Код для авторизации в боте отправлен на email',
                'telegram_code': telegram_code}
        return Response(data, status=status.HTTP_200_OK)

    def create_telegram_code(self, email: str, retry: bool = False) -> int:
        telegram_code = random.randint(100000, 999999)

        if retry:
            TelegramCode.objects.filter(
                email__iexact=email
            ).update(code=telegram_code, created=timezone.now())
            return telegram_code

        TelegramCode.objects.create(email=email, code=telegram_code)
        return telegram_code


class TelegramTokenObtainPairView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TelegramTokenSerializer)
    def post(self, request, *args, **kwargs):
        serializer = TelegramTokenSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        email = serializer.validated_data.get('email')
        telegram_id = serializer.validated_data.get('telegram_id')
        code = serializer.validated_data.get('code')

        user = get_object_or_404(User, email=email)
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        if code:
            user_tg = TelegramUser.objects.filter(user=user)
            if user_tg.exists():
                TelegramUser.objects.filter(user=user).update(
                    telegram_id=telegram_id)
            else:
                TelegramUser.objects.create(user=user, telegram_id=telegram_id)

            TelegramCode.objects.get(email=email).delete()

        data = {'refresh': str(refresh), 'access': access}
        return Response(data=data, status=status.HTTP_200_OK)


class DepartmentViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    filter_backends = (DepartmentInviteCodeFilter, DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = ('id', 'name',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [HRAllPermission | AllReadOnlyPermissions]

    @swagger_auto_schema(manual_parameters=[invite_service.invite_code_param])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PositionViewSet(ModelViewSet):
    serializer_class = PositionSerializer
    queryset = Position.objects.all()
    filter_backends = (PositionInviteCodeFilter, DjangoFilterBackend,)
    filterset_fields = ('id', 'name', 'departments', 'chief_position',)
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [HRAllPermission | AllReadOnlyPermissions]

    @swagger_auto_schema(manual_parameters=[invite_service.invite_code_param])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class HobbyViewSet(ModelViewSet):
    serializer_class = HobbySerializer
    queryset = Hobby.objects.all()
    filter_backends = (DjangoFilterBackend, ElasticSearchFilter)
    filterset_fields = ('id', 'name',)
    search_document = HobbyDocument
    search_fields = ('name',)
    http_method_names = ('get', 'post')
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        return super().get_permissions()
