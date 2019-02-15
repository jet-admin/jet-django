from django.db import transaction
from django.db.models import F
from jet_django.deps.rest_framework import serializers, relations


def reorder_serializer_factory(build_queryset):
    class ReorderSerializer(serializers.Serializer):
        ordering_field = serializers.CharField()
        forward = serializers.BooleanField()
        segment_from = serializers.IntegerField()
        segment_to = serializers.IntegerField()
        item = relations.PrimaryKeyRelatedField(queryset=build_queryset)
        segment_by_ordering_field = serializers.BooleanField(default=False)

        def save(self):
            ordering_field = self.validated_data['ordering_field']

            if self.validated_data.get('segment_by_ordering_field'):
                segment_from = self.validated_data['segment_from']
                segment_to = self.validated_data['segment_to']
            else:
                segment_from_instance = build_queryset.get(pk=self.validated_data['segment_from'])
                segment_to_instance = build_queryset.get(pk=self.validated_data['segment_to'])

                segment_from = getattr(segment_from_instance, ordering_field)
                segment_to = getattr(segment_to_instance, ordering_field)

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
