import django_filters
from django_filters import OrderingFilter


def model_filter_class_factory(build_model, fields):
    def filter_field(field):
        try:
            django_filters.FilterSet.filter_for_field(field, field.name)
            return True
        except AssertionError:
            return False

    filter_fields = list(map(lambda x: x.name, filter(filter_field, fields)))

    class FilterSet(django_filters.FilterSet):
        _order_by = OrderingFilter(fields=filter_fields)

        class Meta:
            model = build_model
            fields = filter_fields

    return FilterSet
