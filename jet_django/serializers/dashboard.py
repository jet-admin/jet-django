from jet_django.deps.rest_framework import serializers

from jet_django.models.dashboard import Dashboard
from jet_django.serializers.widget_list import WidgetListSerializer


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
