import json

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from jet_django.admin.jet import jet
from jet_django.models.model_description import ModelDescription
from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.model_description import ModelDescriptionSerializer


class ModelDescriptionViewSet(viewsets.ModelViewSet):
    model = ModelDescription
    serializer_class = ModelDescriptionSerializer
    queryset = ModelDescription.objects
    pagination_class = None
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def create(self, request, *args, **kwargs):
        try:
            object = self.get_object()
            return super().update(request, *args, **kwargs)
        except Http404:
            return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        def map_override(x):
            try:
                item = json.loads(x.params)
            except ValueError:
                item = {}
            item['app_label'] = x.app_label
            item['model'] = x.model
            return item

        def find_index(ar, x):
            i = 0
            for item in ar:
                if x(item):
                    return i
                else:
                    i += 1

        base = list(map(lambda x: x.serialize(), jet.models))
        overrides = list(map(map_override, self.get_queryset().all()))

        for md_override in overrides:
            md_i = find_index(
                base, lambda x: x.get('app_label') == md_override.get('app_label')
                                              and x.get('model') == md_override.get('model'))

            if md_i is None:
                continue

            for item in ['db_table', 'verbose_name', 'verbose_name_plural', 'hidden', 'ordering_field']:
                if item in base[md_i] and item in md_override:
                    base[md_i][item] = md_override[item]

            md_fields = list(base[md_i]['fields'])

            for field_override in md_override.get('fields', []):
                field_i = find_index(md_fields, lambda x: x.get('name') == field_override.get('name'))

                if field_i is None:
                    continue

                for item in ['verbose_name', 'field', 'editable', 'filterable', 'params']:
                    if item in md_fields[field_i] and item in field_override:
                        md_fields[field_i][item] = field_override[item]

            base[md_i]['fields'] = md_fields

            md_flex_fields = list(base[md_i]['flex_fields'])

            for field_override in md_override.get('flex_fields', []):
                field_i = find_index(md_flex_fields, lambda x: x.get('name') == field_override.get('name'))

                if field_i is None:
                    field = {'name': field_override.get('name')}
                    md_flex_fields.append(field)
                    field_i = len(md_flex_fields) - 1

                for item in ['verbose_name', 'field', 'query', 'code', 'params']:
                    if item in field_override:
                        md_flex_fields[field_i][item] = field_override[item]

            base[md_i]['flex_fields'] = md_flex_fields

            md_relations = list(base[md_i]['relations'])

            for relation_override in md_override.get('relations', []):
                relation_i = find_index(md_relations, lambda x: x.get('name') == relation_override.get('name'))

                if relation_i is None:
                    continue

                for item in ['verbose_name', 'field']:
                    if item in md_relations[relation_i] and item in relation_override:
                        md_relations[relation_i][item] = relation_override[item]

            base[md_i]['relations'] = md_relations

        return Response(base)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {
            'app_label': self.request.data.get('app_label'),
            'model': self.request.data.get('model')
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
