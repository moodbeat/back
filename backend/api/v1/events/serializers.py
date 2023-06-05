from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.v1.users.fields import Base64ImageField
from api.v1.users.serializers import DepartmentSerializer, UserSerializer
from events.models import Category, Entry, Event
from events.validators import validate_event_data

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'role',
            'department', 'position', 'avatar', 'avatar_thumbnail'
        )


class EntryReadSerializer(serializers.ModelSerializer):

    category = CategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = Entry
        fields = '__all__'


class EntryWriteSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    preview_image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Entry
        fields = '__all__'


class EventReadSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()

    class Meta:
        model = Event
        fields = '__all__'


class EventWriteSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    departments = DepartmentSerializer
    employees = UserSerializer

    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        validate_event_data(start_time, end_time)
        return attrs
