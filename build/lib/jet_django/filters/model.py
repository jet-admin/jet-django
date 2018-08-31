from functools import reduce

import django_filters
from django.db.models import Q, fields
from django_filters import filters
from django_filters.constants import EMPTY_VALUES


def model_filter_class_factory(build_model, model_fields):
    model_fields = list(model_fields)

    def filter_field(field):
        try:
            django_filters.FilterSet.filter_for_field(field, field.name)
            return True
        except AssertionError:
            return False

    def search_field(field):
        return isinstance(field, (fields.CharField, fields.TextField))

    search_fields = list(map(lambda x: x.name, filter(search_field, model_fields)))

    filter_field_names = list(map(lambda x: x.name, filter(filter_field, model_fields)))
    filter_fields = dict(map(
        lambda x: [x.name, list(x.get_lookups().keys())],
        filter(lambda x: x.name in filter_field_names, build_model._meta.fields)
    ))

    class SearchFilter(django_filters.CharFilter):

        def filter(self, qs, value):
            if value in EMPTY_VALUES:
                return qs

            query = reduce(lambda q, field: q | Q(**dict([('{}__icontains'.format(field), value)])), search_fields, Q())
            qs = qs.filter(query)

            return qs

    class FilterSet(django_filters.FilterSet):
        _order_by = filters.OrderingFilter(fields=filter_field_names)
        _search = SearchFilter()

        class Meta:
            model = build_model
            fields = filter_fields

    return FilterSet
