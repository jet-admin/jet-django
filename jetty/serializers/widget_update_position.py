from rest_framework import serializers

from jetty.models.widget import Widget


class WidgetUpdatePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = (
            'id',
            'x',
            'y',
            'width',
            'height',
        )
        extra_kwargs = {'id': {'read_only': False}}
