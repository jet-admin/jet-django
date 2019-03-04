from django.db.models import Case, When, Value, IntegerField

from jet_django.deps.rest_framework import serializers


def reset_order_serializer_factory(build_queryset):
    class ResetOrderSerializer(serializers.Serializer):
        ordering_field = serializers.CharField()
        ordering = serializers.CharField(required=False, allow_null=True)
        value_ordering = serializers.CharField(required=False, allow_null=True)

        def save(self):
            ordering_field = self.validated_data['ordering_field']
            ordering = self.validated_data.get('ordering')
            value_ordering = self.validated_data.get('value_ordering')

            qs = build_queryset
            order_by = []

            if value_ordering:
                field, values_str = value_ordering.split('-', 2)
                values = values_str.split(',')
                qs = qs.annotate(
                    __custom_order__=Case(
                        *[When(**dict([(field, x), ('then', Value(i))])) for i, x in enumerate(values)],
                        default=Value(len(values)),
                        output_field=IntegerField(),
                    )
                )
                order_by.append('__custom_order__')

            if ordering:
                order_by.extend(ordering.split(','))

            if len(order_by):
                qs = qs.order_by(*order_by)

            i = 1
            for instance in qs:
                setattr(instance, ordering_field, i)
                instance.save(update_fields=[ordering_field])
                i += 1

    return ResetOrderSerializer
