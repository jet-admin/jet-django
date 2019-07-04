from __future__ import absolute_import, unicode_literals
from functools import reduce
from collections import OrderedDict

from jet_django.deps import django_filters
from django.db import models
from django.db.models import Q, fields, base
from django.contrib.admin.utils import flatten
from jet_django.deps.django_filters import rest_framework as filters
from jet_django.deps.django_filters.constants import EMPTY_VALUES
from django.db.models.fields.related import ForeignObjectRel
from jet_django.deps.django_filters.utils import resolve_field, get_model_field
from jet_django.filters.geos_geometry import GEOSGeometryFilter
from jet_django.serializers.sql import SqlSerializer


def model_filter_class_factory(build_model, model_fields, model_relations):
    model_fields = list(model_fields)

    def filter_field(field):
        try:
            from django.contrib.gis.db.models import PointField
            if isinstance(field, PointField):
                return True
        except:
            pass

        try:
            django_filters.FilterSet.filter_for_field(field, field.name)
            return True
        except:
            return False

    def search_field(field):
        allowed_fields = [
            fields.CharField,
            fields.TextField,
            fields.IPAddressField,
            fields.GenericIPAddressField,
            fields.UUIDField
        ]

        try:
            from django.contrib.postgres.fields import JSONField
            allowed_fields.append(JSONField)
        except ImportError:
            pass

        return isinstance(field, tuple(allowed_fields))

    def foreign_key_field(field):
        return isinstance(field, (fields.related.ForeignKey,)) and isinstance(field.related_model, (base.ModelBase,))

    def foreign_key_map(field):
        field_fields = field.related_model._meta.get_fields()
        return list(map(lambda x: '{}__{}'.format(field.name, x.name), filter(search_field, field_fields)))

    search_fields = list(map(lambda x: x.name, filter(search_field, model_fields)))
    search_related_fields = flatten(list(map(foreign_key_map, filter(foreign_key_field, model_fields))))

    search_fields = search_fields + search_related_fields

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

    class ModelSegmentFilter(django_filters.CharFilter):

        def filter(self, qs, value):
            if value in EMPTY_VALUES:
                return qs

            body = self.parent.request.data

            if not isinstance(body, dict):
                return qs.none()

            items = list(filter(lambda x: x.get('name') == value, body.get('segments', [])))

            if len(items) == 0:
                return qs.none()

            query = items[0].get('query')

            serializer = SqlSerializer(data={'query': query})
            serializer.is_valid(raise_exception=True)
            result = serializer.execute(serializer.validated_data)
            columns = list(result['columns'])
            rows = result['data']

            if len(columns) == 0 or len(rows) == 0:
                return qs.none()

            ids = list(map(lambda x: list(x)[0], rows))

            return qs.filter(pk__in=ids)

    class ModelRelationFilter(django_filters.CharFilter):

        def filter(self, qs, value):
            if value in EMPTY_VALUES:
                return qs

            from django.apps import apps
            models = apps.get_models()

            def get_model(app_label, model):
                result = list(filter(lambda x: x._meta.app_label == app_label and x._meta.model_name == model, models))
                return result[0] if len(result) else None

            def get_field_column(model, field_name):
                field = model._meta.get_field(field_name)
                return field.get_attname_column()[1]

            current_table = build_model
            path = list(map(lambda x: x.split('.'), value.split('|')))
            path_len = len(path)

            sql = list()
            args = list()

            sql.append('SELECT {0}.{1} as id FROM {0}'.format(build_model._meta.db_table, build_model._meta.pk.name))

            for i in range(path_len):
                item = path[i]
                last = i == path_len - 1

                if not last:
                    current_table_column = get_field_column(current_table, item[0])
                    related_table = get_model(*item[1].split(';'))
                    related_table_column = get_field_column(related_table, item[2])

                    sql.append('JOIN {2} ON {0}.{1} = {2}.{3}'.format(
                        current_table._meta.db_table,
                        current_table_column,
                        related_table._meta.db_table,
                        related_table_column
                    ))
                    current_table = related_table
                else:
                    current_table_column = get_field_column(current_table, item[0])
                    sql.append(' WHERE {0}.{1} IN (%s)'.format(current_table._meta.db_table, current_table_column))
                    args.append(item[1])

            query = build_model.objects.raw(' '.join(sql), args)
            pks = list(map(lambda x: x.pk, query))
            return qs.filter(pk__in=pks)

    filter_overrides_value = {
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
        models.BooleanField: {
            'filter_class': filters.BooleanFilter
        }
    }

    try:
        from django.contrib.gis.db.models import PointField
        filter_overrides_value[PointField] = {
            'filter_class': GEOSGeometryFilter
        }
    except:
        pass

    class FilterSet(django_filters.FilterSet):
        _order_by = filters.OrderingFilter(fields=filter_field_names)
        _search = SearchFilter()
        _m2m = M2MFilter()
        _segment = ModelSegmentFilter()
        _relation = ModelRelationFilter()

        class Meta:
            model = build_model
            fields = filter_fields
            filter_overrides = filter_overrides_value

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

                for lookup_expr in lookups:
                    filter_name = cls.get_filter_name(field_name, lookup_expr)

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
        def filter_for_field(cls, field, field_name, lookup_expr='exact', exclude=False):
            field, lookup_type = resolve_field(field, lookup_expr)

            default = {
                'field_name': field_name,
                'lookup_expr': lookup_expr,
                'exclude': exclude
            }

            filter_class, params = cls.filter_for_lookup(field, lookup_type)
            default.update(params)

            assert filter_class is not None, (
                                                 "%s resolved field '%s' with '%s' lookup to an unrecognized field "
                                                 "type %s. Try adding an override to 'Meta.filter_overrides'. See: "
                                                 "https://django-filter.readthedocs.io/en/master/ref/filterset.html"
                                                 "#customise-filter-generation-with-filter-overrides"
        ) % (cls.__name__, field_name, lookup_expr, field.__class__.__name__)

            return filter_class(**default)

    return FilterSet
