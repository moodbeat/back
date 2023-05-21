from django.contrib.auth import get_user_model
from rest_framework import serializers
from socials.models import HelpType, NeedHelp

User = get_user_model()


class SpecialistsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'patronymic', 'role',
            'department', 'position', 'avatar'
        )


class HelpTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = HelpType
        fields = '__all__'


class NeedHelpSerializer(serializers.ModelSerializer):

    class Meta:
        models = NeedHelp
        fields = '__all__'
