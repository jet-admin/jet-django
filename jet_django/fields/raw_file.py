from jet_django.deps.rest_framework import serializers


class RawFileField(serializers.CharField):

    def __init__(self, *args, **kwargs):
        if 'validators' in kwargs:
            del kwargs['validators']
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        return {
            'value': super().to_representation(value),
            'url': serializers.FileField.to_representation(self, value)
        }
