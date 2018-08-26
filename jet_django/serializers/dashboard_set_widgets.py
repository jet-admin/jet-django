from django.db import transaction
from rest_framework import serializers

from jet_django.models.dashboard import Dashboard
from jet_django.models.widget import Widget
from jet_django.serializers.widget_update_position import WidgetUpdatePositionSerializer


class DashboardSetWidgetsSerializer(serializers.ModelSerializer):
    widgets = WidgetUpdatePositionSerializer(many=True)

    class Meta:
        model = Dashboard
        fields = (
            'widgets',
        )

    def update(self, instance, validated_data):
        with transaction.atomic():
            widgets = Widget.objects.filter(dashboard=instance)

            for widget in validated_data['widgets']:
                widgets.filter(pk=widget['id']).update(
                    x=widget['x'],
                    y=widget['y'],
                    width=widget['width'],
                    height=widget['height'],
                    params=widget['params']
                )

            widgets.exclude(pk__in=map(lambda x: x['id'], validated_data['widgets'])).delete()

        return instance
