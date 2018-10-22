from django.db import connection, DatabaseError
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from jet_django.deps.rest_framework import serializers, status
from jet_django.deps.rest_framework.exceptions import ValidationError, APIException


class ParamsSerializers(serializers.CharField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return list(filter(lambda x: x != '', value.split(',')))

    def to_representation(self, value):
        return list(value)


class SqlError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Query failed')
    default_code = 'invalid'

    def __init__(self, detail):
        self.detail = {'error': str(detail)}

    def __str__(self):
        return six.text_type(self.detail)


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

    def execute(self):
        with connection.cursor() as cursor:
            try:
                cursor.execute(self.validated_data['query'], self.validated_data.get('params', []))
            except (DatabaseError, TypeError) as e:
                raise SqlError(e)

            rows = cursor.fetchall()

            def map_column(x):
                if x.name == '?column?':
                    return
                return x.name

            return {'data': rows, 'columns': map(map_column, cursor.description)}
