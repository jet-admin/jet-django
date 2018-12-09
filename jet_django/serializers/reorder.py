from django.db import transaction
from django.db.models import F
from jet_django.deps.rest_framework import serializers, relations


def reorder_serializer_factory(build_queryset):
    class ReorderSerializer(serializers.Serializer):
        ordering_field = serializers.CharField()
        forward = serializers.BooleanField()
        segment_from = relations.PrimaryKeyRelatedField(queryset=build_queryset)
        segment_to = relations.PrimaryKeyRelatedField(queryset=build_queryset)
        item = relations.PrimaryKeyRelatedField(queryset=build_queryset)

        def save(self):
            ordering_field = self.validated_data['ordering_field']
            segment_from = getattr(self.validated_data['segment_from'], ordering_field)
            segment_to = getattr(self.validated_data['segment_to'], ordering_field)

            with transaction.atomic():
                if self.validated_data['forward']:
                    build_queryset.filter(
                        **{
                            '{}__gte'.format(ordering_field): segment_from,
                            '{}__lte'.format(ordering_field): segment_to
                        }
                    ).update(
                        **{ordering_field: F(ordering_field) - 1}
                    )
                    build_queryset.filter(
                        pk=self.validated_data['item'].pk
                    ).update(
                        **{ordering_field: segment_to}
                    )
                else:
                    build_queryset.filter(
                        **{
                            '{}__gte'.format(ordering_field): segment_from,
                            '{}__lte'.format(ordering_field): segment_to
                        }
                    ).update(
                        **{ordering_field: F(ordering_field) + 1}
                    )
                    build_queryset.filter(
                        pk=self.validated_data['item'].pk
                    ).update(
                        **{ordering_field: segment_from}
                    )

    return ReorderSerializer
