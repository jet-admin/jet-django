from jet_django.deps.rest_framework import serializers

from jet_django.models.model_description import ModelDescription


class ModelDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelDescription
        fields = (
            'app_label',
            'model',
            'params',
            'date_add'
        )
