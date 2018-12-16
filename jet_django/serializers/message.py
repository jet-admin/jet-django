from jet_django.admin.jet import jet
from jet_django.deps.rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    name = serializers.CharField()
    params = serializers.JSONField(required=False, default={})

    def save(self, **kwargs):
        handler = jet.get_message_handler(self.validated_data['name'])

        if not handler:
            return

        return handler(self.validated_data.get('params'))
