from rest_framework import serializers

from jet_django.models.widget import Widget


class WidgetUpdatePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = (
            'id',
            'x',
            'y',
            'width',
            'height',
            'params'
        )
        extra_kwargs = {'id': {'read_only': False}}
