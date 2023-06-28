from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from sorl.thumbnail import get_thumbnail

from api.v1.socials.serializers import LikeShortSerializer
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

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'avatar', 'avatar_full'
        )

    def get_avatar(self, obj):
        if obj.avatar_full:
            return get_thumbnail(
                obj.avatar_full, '120x120', crop='center', quality=99
            ).url
        return None


class WithLikedSerializer(serializers.ModelSerializer):

    liked = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=LikeShortSerializer)
    def get_liked(self, obj):
        liked = obj.likes.filter(employee=self.context['request'].user).first()
        if not liked:
            return None
        return LikeShortSerializer(liked).data


class EntryReadSerializer(WithLikedSerializer):

    category = CategorySerializer(many=True)
    author = AuthorSerializer()

    class Meta:
        model = Entry
        fields = '__all__'


class EntryWriteSerializer(serializers.ModelSerializer):

    category = CategorySerializer
    preview_image = Base64ImageField(required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Entry
        fields = '__all__'

    def validate(self, data):
        text = data.get('text', None)
        url = data.get('url', None)

        if not text and not url:
            raise ValidationError(
                'Запись обязательно должна содержать ссылку или текст.'
            )

        if text and url:
            raise ValidationError(
                'Введите что-то одно (текст или ссылку).'
            )

        return data


class EventReadSerializer(WithLikedSerializer):

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
