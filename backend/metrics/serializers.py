from rest_framework import serializers

from .models import Condition


class ConditionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Condition
        fields = ['id', 'user', 'mood', 'note', 'date']
