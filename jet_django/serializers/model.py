from django.db import models
from rest_framework import serializers

from jet_django.fields.raw_file import RawFileField


def model_serializer_factory(build_model, build_fields):
    class Serializer(serializers.ModelSerializer):

        class Meta:
            model = build_model
            fields = build_fields + ['__str__']

        def __new__(cls, *args, **kwargs):
            cls.serializer_field_mapping[models.FileField] = RawFileField
            cls.serializer_field_mapping[models.ImageField] = RawFileField
            return super(Serializer, cls).__new__(cls, *args, **kwargs)

    return Serializer
