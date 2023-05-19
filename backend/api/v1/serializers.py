from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from users.models import Department, Hobby, Position, User

from .fields import Base64ImageField


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ('id', 'name',)


class HobbySerializer(serializers.ModelSerializer):

    class Meta:
        model = Hobby
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    hobbies = HobbySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'patronymic', 'role',
            'department', 'position', 'hobbies', 'avatar', 'about', 'phone',
            'date_joined'
        )


class UserSelfUpdateSerializer(serializers.ModelSerializer):
    '''Для редактирования своего профиля'''

    avatar = Base64ImageField()
    hobbies = HobbySerializer

    class Meta:
        model = User
        fields = ('about', 'avatar', 'hobbies')


class UserUpdateSerializer(serializers.ModelSerializer):
    '''Для редактирования профилей сотрудников HR'ом'''

    department = DepartmentSerializer
    position = PositionSerializer
    role = serializers.ChoiceField(choices=['employee', 'chief'])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic',
                  'department', 'position', 'role', 'phone')


class SendInviteSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    class Meta:
        fields = ('email',)


class RegisterSerializer(serializers.Serializer):

    invite_code = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=True
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(), required=True
    )

    class Meta:
        fields = ('invite_code', 'first_name',
                  'last_name', 'department', 'position', 'password')

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_position(self, value):
        department = self.initial_data.get('department')
        if department:
            if not value.departments.filter(pk=department).exists():
                raise serializers.ValidationError(
                    "Выбранная должность не принадлежит к указанному отделу.")
        return value


class VerifyInviteSerializer(serializers.Serializer):

    invite_code = serializers.CharField(required=True)

    class Meta:
        fields = ('invite_code',)
