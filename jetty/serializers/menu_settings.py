from rest_framework import serializers

from jetty.models.menu_item import MenuSettings


class MenuSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuSettings
        fields = (
            'items',
            'date_add'
        )
