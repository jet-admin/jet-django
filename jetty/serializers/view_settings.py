from rest_framework import serializers

from jetty.models.view_settings import ViewSettings


class ViewSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewSettings
        fields = (
            'app_label',
            'model',
            'layout',
            'date_add'
        )
