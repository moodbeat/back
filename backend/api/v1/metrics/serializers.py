from rest_framework import serializers

from metrics.models import Condition


class ConditionReadSerializer(serializers.ModelSerializer):
    # employee = serializers.StringRelatedField()

    class Meta:
        model = Condition
        fields = ['id', 'employee', 'mood', 'note', 'date']


class ConditionWriteSerializer(serializers.ModelSerializer):
    # employee = serializers.StringRelatedField()

    class Meta:
        model = Condition
        fields = ['id', 'employee', 'mood', 'note', 'date']