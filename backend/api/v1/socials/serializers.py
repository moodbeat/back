from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from sorl.thumbnail import get_thumbnail

from socials.models import HelpType, Like, NeedHelp, Status

User = get_user_model()


class SpecialistsSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'patronymic', 'role',
            'department', 'position', 'avatar', 'avatar_full'
        )

    def get_avatar(self, obj):
        if obj.avatar_full:
            return get_thumbnail(
                obj.avatar_full, '120x120', crop='center', quality=99
            ).url
        return None


class HelpTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = HelpType
        fields = '__all__'


class NeedHelpSerializer(serializers.ModelSerializer):

    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    viewed = serializers.BooleanField(read_only=True)

    class Meta:
        model = NeedHelp
        fields = '__all__'

    def validate(self, data):
        sender = data.get('sender')
        recipient = data.get('recipient')

        if sender == recipient:
            raise serializers.ValidationError(
                'Нельзя отправлять запрос самому себе.'
            )

        if not recipient.is_hr and not recipient.is_chief:
            raise serializers.ValidationError(
                'Принимающая сторона должна быть HR или руководителем.'
            )

        return data


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ('text', 'views', 'likes', 'created')


class StatusAddSerializer(StatusSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Status
        fields = '__all__'
        read_only_fields = ('views', 'likes')


class LikeSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = '__all__'

    def validate(self, data):
        event = data.get('event', None)
        entry = data.get('entry', None)

        if not event and not entry:
            raise ValidationError('Выберите Событие или Запись.')

        if event and entry:
            raise ValidationError('Выберите что-то одно.')

        return data


class LikeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ('id', 'created')
