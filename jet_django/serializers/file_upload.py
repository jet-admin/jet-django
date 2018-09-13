import os

from django.core.exceptions import SuspiciousFileOperation, ValidationError
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    path = serializers.CharField(write_only=True)
    filename = serializers.CharField(write_only=True, required=False)
    uploaded_path = serializers.CharField(read_only=True)

    def validate(self, attrs):
        if attrs.get('filename') is None:
            attrs['filename'] = attrs['file'].name

        attrs['full_path'] = os.path.join(attrs['path'], attrs['filename'])

        try:
            default_storage.get_available_name(attrs['full_path'])
        except SuspiciousFileOperation:
            raise ValidationError(_('forbidden path'))

        return attrs

    def save(self, **kwargs):
        uploaded_path = default_storage.save(self.validated_data['full_path'], self.validated_data['file'])

        self.instance = {
            'uploaded_path': uploaded_path
        }
