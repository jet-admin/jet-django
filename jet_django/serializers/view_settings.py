from jet_django.deps.rest_framework import serializers

from jet_django.models.view_settings import ViewSettings


class ViewSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewSettings
        fields = (
            'app_label',
            'model',
            'view',
            'params',
            'date_add'
        )
