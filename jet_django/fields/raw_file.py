from rest_framework import serializers


class RawFileField(serializers.CharField):

    def to_representation(self, value):
        return serializers.FileField.to_representation(self, value)
