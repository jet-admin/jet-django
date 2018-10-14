import json
from django.utils.translation import ugettext_lazy as _

from jet_django.deps.rest_framework import serializers


class RawFileField(serializers.CharField):

    def __init__(self, *args, **kwargs):
        if 'validators' in kwargs:
            del kwargs['validators']

        self.default_error_messages['invalid_format'] = _('Not a valid format.')
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            obj = data
        else:
            try:
                obj = json.loads(data)
            except (ValueError, TypeError):
                self.fail('invalid_format')

        try:
            return obj['value']
        except KeyError:
            self.fail('invalid_format')

    def to_representation(self, value):
        return {
            'value': super().to_representation(value),
            'url': serializers.FileField.to_representation(self, value)
        }
