from jet_django.deps.rest_framework import serializers

from jet_django.models.menu_item import MenuSettings


class MenuSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuSettings
        fields = (
            'items',
            'date_add'
        )
