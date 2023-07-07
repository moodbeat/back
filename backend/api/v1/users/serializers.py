from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)
from sorl.thumbnail import get_thumbnail

from api.v1.metrics.serializers import ConditionReadSerializer
from users.models import Department, Hobby, MentalState, Position

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
        fields = '__all__'


class MentalStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MentalState
        exclude = ('id',)


class UserSerializer(serializers.ModelSerializer):

    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    mental_state = MentalStateSerializer(read_only=True)
    hobbies = HobbySerializer(many=True, read_only=True)
    latest_condition = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'patronymic', 'role',
            'avatar', 'avatar_full', 'about', 'phone', 'date_joined',
            'mental_state', 'latest_condition', 'position', 'department',
            'hobbies',
        )

    @swagger_serializer_method(serializer_or_field=ConditionReadSerializer)
    def get_latest_condition(self, obj):
        latest_condition = obj.condition_set.order_by('-date').first()
        if not latest_condition:
            return None
        return ConditionReadSerializer(latest_condition).data

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


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        raise InvalidToken(
            'No valid token found in cookie \'refresh_token\''
        )
