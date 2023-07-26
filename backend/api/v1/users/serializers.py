from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from sorl.thumbnail import get_thumbnail

from api.v1.metrics.serializers import ConditionReadSerializer
from metrics.models import ActivityTracker
from users.models import (Department, Hobby, MentalState, Position,
                          TelegramCode, TelegramUser)

from .fields import Base64ImageField

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ('id', 'name', 'chief_position', 'departments')


class HobbySerializer(serializers.ModelSerializer):

    class Meta:
        model = Hobby
        fields = ['id', 'name']


class MentalStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MentalState
        exclude = ('id',)


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityTracker
        exclude = ('employee',)


class UserSerializer(serializers.ModelSerializer):

    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    mental_state = MentalStateSerializer(read_only=True)
    hobbies = HobbySerializer(many=True, read_only=True)
    latest_condition = serializers.SerializerMethodField()
    latest_activity = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'patronymic', 'role',
            'avatar', 'avatar_full', 'about', 'phone', 'date_joined',
            'mental_state', 'latest_condition', 'latest_activity', 'position',
            'department', 'hobbies',
        )

    @swagger_serializer_method(serializer_or_field=ConditionReadSerializer)
    def get_latest_condition(self, obj):
        latest_condition = obj.condition_set.order_by('-date').first()
        if not latest_condition:
            return None
        return ConditionReadSerializer(latest_condition).data

    @swagger_serializer_method(serializer_or_field=ActivitySerializer)
    def get_latest_activity(self, obj):
        latest_activity = obj.activity_trackers.order_by('-date').first()
        if not latest_activity:
            return None
        return ActivitySerializer(latest_activity).data

    def get_avatar(self, obj):
        if obj.avatar_full:
            return get_thumbnail(
                obj.avatar_full, '120x120', crop='center', quality=99
            ).url
        return None


class UserSelfUpdateSerializer(serializers.ModelSerializer):
    """Для редактирования своего профиля."""

    avatar = Base64ImageField()
    hobbies = HobbySerializer

    class Meta:
        model = User
        fields = ('about', 'avatar', 'hobbies')

    def update(self, instance, validated_data):
        if 'avatar' in validated_data:
            instance.avatar_full = validated_data['avatar']
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Для редактирования профилей сотрудников HR'ом."""

    department = DepartmentSerializer
    position = PositionSerializer
    role = serializers.ChoiceField(choices=['employee', 'chief'])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic',
                  'department', 'position', 'role', 'phone')

    def validate(self, data):
        if self.instance and self.instance.is_hr:
            raise serializers.ValidationError(
                'Нельзя редактировать сотрудника с ролью HR.'
            )
        return data

    def validate_position(self, value):
        department = self.initial_data.get('department')
        position = self.initial_data.get('position')

        if position is None:
            return value

        if department:
            if not value.departments.filter(pk=department).exists():
                raise serializers.ValidationError(
                    'Выбранная должность не относится к указанному отделу.'
                )

        user_department = self.instance.department

        if user_department and not department:
            if not value.departments.filter(pk=user_department.pk).exists():
                raise serializers.ValidationError(
                    'Выбранная должность не относится к текущему отделу '
                    'пользователя.'
                )
        else:
            self.initial_data.pop('position')

        return value

    def validate_department(self, value):
        department = self.initial_data.get('department')
        position = self.initial_data.get('position')
        # даааа это рефакторить, помогите или убейте меня хахах
        if department is None and position:
            self.initial_data.pop('position', None)

        user = self.instance

        if department is None and user.position or position is None:
            user.position = None
            user.save()

        return value


class SendInviteSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',)


class PasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Пользователь с указанным email адресом отсутствует.'
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):

    reset_code = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    class Meta:
        fields = ('reset_code', 'password', 'password_confirm')

    def validate_password(self, value):
        password_confirm = self.initial_data.get('password_confirm')

        if password_confirm != value:
            raise serializers.ValidationError('Пароли не совпадают.')

        validate_password(value)
        return value


class PasswordChangeSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    class Meta:
        fields = ('current_password', 'new_password', 'new_password_confirm')

    def validate_new_password(self, value):
        password_confirm = self.initial_data.get('new_password_confirm')

        if password_confirm != value:
            raise serializers.ValidationError('Пароли не совпадают.')

        validate_password(value)
        return value


class RegisterSerializer(serializers.ModelSerializer):

    invite_code = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=True
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(), required=True
    )

    class Meta:
        model = User
        fields = ('invite_code', 'first_name', 'last_name',
                  'department', 'position', 'password', 'password_confirm')

    def validate(self, data):
        password_confirm = data.get('password_confirm')
        password = data.get('password')

        if password_confirm != password:
            raise serializers.ValidationError('Пароли не совпадают.')

        validate_password(password)
        data.pop('password_confirm')
        return data

    def validate_position(self, value):
        department = self.initial_data.get('department')

        if department:
            if not value.departments.filter(pk=department).exists():
                raise serializers.ValidationError(
                    'Выбранная должность не относится к указанному отделу.'
                )

            if value.chief_position is True:
                raise serializers.ValidationError(
                    'Нельзя выбирать при регистрации руководящую должность.'
                )

        return value


class VerifyInviteSerializer(serializers.Serializer):

    invite_code = serializers.CharField(required=True)

    class Meta:
        fields = ('invite_code',)


class CustomTokenObtainSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        attrs["email"] = attrs.get("email").lower()
        return super(CustomTokenObtainSerializer, self).validate(attrs)


class TelegramTokenSerializer(serializers.Serializer):

    email = serializers.EmailField()
    code = serializers.IntegerField(required=False)
    telegram_id = serializers.IntegerField()

    def validate(self, data):
        email = data.get('email')
        telegram_id = data.get('telegram_id')
        code = data.get('code', None)

        user = User.objects.filter(email=email)
        if not user.exists():
            raise serializers.ValidationError(
                'Пользователь с указанным email не найден.'
            )

        if code:
            telegram_code = TelegramCode.objects.filter(email=email, code=code)
            if not telegram_code.exists():
                raise serializers.ValidationError('Недействительный код.')

            difference = timezone.now() - telegram_code.first().created
            time_expires = int(settings.BOT_INVITE_TIME_EXPIRES_MINUTES)
            if difference > timezone.timedelta(minutes=time_expires):
                raise serializers.ValidationError(
                    'Время действия кода истекло.'
                )
        else:
            user = TelegramUser.objects.filter(
                user__email=email, telegram_id=telegram_id
            )
            if not user.exists():
                raise serializers.ValidationError(
                    'Пользователь с указанными парой email/telegram_id не '
                    'найден. Получите на email код для авторизации и '
                    'попробуйте снова с использованием поля code.'
                )

        return data
