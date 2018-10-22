from jet_django.deps.rest_framework import serializers
from jet_django.deps.rest_framework.exceptions import ValidationError


class ParamsSerializers(serializers.CharField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return list(filter(lambda x: x != '', value.split(',')))

    def to_representation(self, value):
        return list(value)


class SqlSerializer(serializers.Serializer):
    query = serializers.CharField()
    params = ParamsSerializers(required=False)

    def validate_query(self, value):
        forbidden = ['insert', 'update', 'delete', 'grant', 'show']
        for i in range(len(forbidden)):
            forbidden.append('({}'.format(forbidden[i]))
        if any(map(lambda x: ' {} '.format(value.lower()).find(' {} '.format(x)) != -1, forbidden)):
            raise ValidationError('forbidden query')
        return value
