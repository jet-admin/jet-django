from rest_framework import serializers

from jet_django.utils.siblings import get_model_sibling


def model_detail_serializer_factory(build_model, build_fields):
    class Serializer(serializers.ModelSerializer):
        __previous_sibling__ = serializers.SerializerMethodField('get_previous_sibling')
        __next_sibling__ = serializers.SerializerMethodField('get_next_sibling')

        class Meta:
            model = build_model
            fields = build_fields + ['__str__', '__previous_sibling__', '__next_sibling__']

        def sibling_response(self, sibling):
            if not sibling:
                return
            return {
                'id': sibling.pk,
                '__str__': str(sibling)
            }

        def get_previous_sibling(self, instance, ordering=None):
            sibling = get_model_sibling(build_model, instance, False, ordering)
            return self.sibling_response(sibling)

        def get_next_sibling(self, instance, ordering=None):
            sibling = get_model_sibling(build_model, instance, True, ordering)
            return self.sibling_response(sibling)

    return Serializer
