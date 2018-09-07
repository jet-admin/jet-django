from __future__ import absolute_import, unicode_literals
from functools import reduce
from collections import OrderedDict

import django_filters
from django.db import models
from django.db.models import Q, fields
from django_filters import filters
from django_filters.constants import EMPTY_VALUES
from django.db.models.fields.related import ForeignObjectRel
from django_filters.utils import resolve_field, get_model_field
from django_filters.filterset import get_filter_name


def model_filter_class_factory(build_model, model_fields, model_relations):
    model_fields = list(model_fields)

    def filter_field(field):
        try:
            django_filters.FilterSet.filter_for_field(field, field.name)
            return True
        except:
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

    class M2MFilter(django_filters.CharFilter):

        def filter(self, qs, value):
            if value in EMPTY_VALUES:
                return qs

            params = value.split(',', 2)

            if len(params) < 2:
                return qs.none()

            relation_name, value = params
            relations = list(filter(lambda x: x.name == relation_name, model_relations))

            if len(relations) == 0:
                return qs.none()

            relation = relations[0]

            if isinstance(relation, models.ManyToManyRel):
                query = {'{}__pk'.format(relation_name): value}
                qs = qs.filter(**query)
            elif isinstance(relation, models.ManyToManyField):
                query = {'{}__pk'.format(relation_name): value}
                qs = qs.filter(**query)

            return qs

    class FilterSet(django_filters.FilterSet):
        _order_by = filters.OrderingFilter(fields=filter_field_names)
        _search = SearchFilter()
        _m2m = M2MFilter()

        class Meta:
            model = build_model
            fields = filter_fields
            filter_overrides = {
                models.DateTimeField: {
                    'filter_class': filters.DateTimeFilter,
                    'extra': lambda f: {
                        'input_formats': ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ']
                    }
                },
                models.DateField: {
                    'filter_class': filters.DateFilter,
                    'extra': lambda f: {
                        'input_formats': ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ']
                    }
                },
            }

        @classmethod
        def get_filters(cls):
            """
            Get all filters for the filterset. This is the combination of declared and
            generated filters.
            """

            # No model specified - skip filter generation
            if not cls._meta.model:
                return cls.declared_filters.copy()

            # Determine the filters that should be included on the filterset.
            filters = OrderedDict()
            fields = cls.get_fields()
            undefined = []

            for field_name, lookups in fields.items():
                field = get_model_field(cls._meta.model, field_name)

                # warn if the field doesn't exist.
                if field is None:
                    undefined.append(field_name)

                # ForeignObjectRel does not support non-exact lookups
                if isinstance(field, ForeignObjectRel):
                    filters[field_name] = cls.filter_for_reverse_field(field, field_name)
                    continue

                for lookup_expr in lookups:
                    filter_name = get_filter_name(field_name, lookup_expr)

                    # If the filter is explicitly declared on the class, skip generation
                    if filter_name in cls.declared_filters:
                        filters[filter_name] = cls.declared_filters[filter_name]
                        continue

                    if field is not None:
                        filters[filter_name] = cls.filter_for_field(field, field_name, lookup_expr)
                        filters['exclude__{}'.format(filter_name)] = cls.filter_for_field(field, field_name, lookup_expr, exclude=True)

            # filter out declared filters
            undefined = [f for f in undefined if f not in cls.declared_filters]
            if undefined:
                raise TypeError(
                    "'Meta.fields' contains fields that are not defined on this FilterSet: "
                    "%s" % ', '.join(undefined)
                )

            # Add in declared filters. This is necessary since we don't enforce adding
            # declared filters to the 'Meta.fields' option
            filters.update(cls.declared_filters)
            return filters

        @classmethod
        def filter_for_field(cls, f, name, lookup_expr='exact', exclude=False):
            f, lookup_type = resolve_field(f, lookup_expr)

            default = {
                'name': name,
                'lookup_expr': lookup_expr,
                'exclude': exclude
            }

            filter_class, params = cls.filter_for_lookup(f, lookup_type)
            default.update(params)

            assert filter_class is not None, (
                                                 "%s resolved field '%s' with '%s' lookup to an unrecognized field "
                                                 "type %s. Try adding an override to 'Meta.filter_overrides'. See: "
                                                 "https://django-filter.readthedocs.io/en/develop/ref/filterset.html#customise-filter-generation-with-filter-overrides"
                                             ) % (cls.__name__, name, lookup_expr, f.__class__.__name__)

            return filter_class(**default)

    return FilterSet
