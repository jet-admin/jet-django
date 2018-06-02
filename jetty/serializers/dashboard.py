from rest_framework import serializers

from jetty.models.dashboard import Dashboard
from jetty.serializers.widget_list import WidgetListSerializer


class DashboardSerializer(serializers.ModelSerializer):
    widgets = WidgetListSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = (
            'id',
            'name',
            'ordering',
            'date_add',
            'widgets'
        )
