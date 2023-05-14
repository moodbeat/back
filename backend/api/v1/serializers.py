from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from users.models import Department, Hobby, Position, User


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


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
            'position', 'department', 'hobbies', 'avatar', 'about', 'phone',
            'date_joined'
        )


class SendInviteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ('email',)


class RegisterSerializer(serializers.Serializer):
    invite_code = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        fields = ('invite_code', 'first_name', 'last_name', 'password')

    def validate_password(self, value):
        validate_password(value)
        return value
