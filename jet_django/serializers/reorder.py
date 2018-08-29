from django.db import transaction
from django.db.models import F
from rest_framework import serializers, relations


def reorder_serializer_factory(build_queryset, ordering_field):
    class ReorderSerializer(serializers.Serializer):
        forward = serializers.BooleanField()
        segment_from = relations.PrimaryKeyRelatedField(queryset=build_queryset)
        segment_to = relations.PrimaryKeyRelatedField(queryset=build_queryset)
        item = relations.PrimaryKeyRelatedField(queryset=build_queryset)

        def save(self):
            with transaction.atomic():
                if self.validated_data['forward']:
                    build_queryset.filter(
                        **{
                            '{}__gte'.format(ordering_field): getattr(self.validated_data['segment_from'], ordering_field),
                            '{}__lte'.format(ordering_field): getattr(self.validated_data['segment_to'], ordering_field)
                        }
                    ).update(
                        **{ordering_field: F(ordering_field) - 1}
                    )
                    build_queryset.filter(
                        pk=self.validated_data['item'].pk
                    ).update(
                        **{ordering_field: getattr(self.validated_data['segment_to'], ordering_field)}
                    )
                else:
                    build_queryset.filter(
                        **{
                            '{}__gte'.format(ordering_field): getattr(self.validated_data['segment_from'], ordering_field),
                            '{}__lte'.format(ordering_field): getattr(self.validated_data['segment_to'], ordering_field)
                        }
                    ).update(
                        **{ordering_field: F(ordering_field) + 1}
                    )
                    build_queryset.filter(
                        pk=self.validated_data['item'].pk
                    ).update(
                        **{ordering_field: getattr(self.validated_data['segment_from'], ordering_field)}
                    )

    return ReorderSerializer
