from jet_django.deps.rest_framework import serializers


def model_detail_serializer_factory(build_model, build_fields):
    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = build_model
            fields = build_fields + ['__str__']

    return Serializer
