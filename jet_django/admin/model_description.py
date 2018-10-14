from django.contrib.contenttypes.fields import GenericRel, GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from jet_django.filters.model import model_filter_class_factory
from jet_django.serializers.model import model_serializer_factory
from jet_django.serializers.model_detail import model_detail_serializer_factory
from jet_django.views.model import model_viewset_factory


class JetAdminModelDescription(object):
    def __init__(self, Model, fields=None, actions=list(), ordering_field=None, hidden=False):
        self.model = Model
        self.fields = fields
        self.hidden = hidden

        for action in actions:
            action.init_meta()

        self.actions = actions
        self.ordering_field = ordering_field \
            if ordering_field in map(lambda x: x.name, self.get_model_fields()) \
            else None
        self.content_type = ContentType.objects.get_for_model(Model)
        self.field_names = list(map(lambda x: x.name, self.get_display_model_fields()))
        self.serializer = model_serializer_factory(Model, self.field_names)
        self.detail_serializer = model_detail_serializer_factory(Model, self.field_names)
        self.filter_class = model_filter_class_factory(Model, self.get_display_model_fields(), self.get_model_relations())
        self.queryset = Model.objects.all()
        self.viewset = model_viewset_factory(
            Model,
            self.filter_class,
            self.serializer,
            self.detail_serializer,
            self.queryset,
            self.actions,
            self.ordering_field
        )

    @property
    def viewset_url(self):
        return 'models/(?P<app_label>{})/(?P<model>{})'.format(self.content_type.app_label, self.content_type.model)

    def get_model_fields(self):
        fields = self.model._meta.get_fields()
        def filter_fields(x):
            if any(map(lambda rel: isinstance(x, rel), [
                models.OneToOneRel,
                models.OneToOneField,
                models.ManyToOneRel,
                models.ManyToManyField,
                models.ManyToManyRel,
                GenericRel,
                GenericForeignKey,
                GenericRelation
            ])):
                return False
            return True
        return filter(filter_fields, fields)

    def get_model_relations(self):
        fields = self.model._meta.get_fields(include_hidden=True)
        def filter_fields(x):
            if any(map(lambda rel: isinstance(x, rel), [
                models.OneToOneRel,
                models.OneToOneField,
                models.ManyToOneRel,
                models.ManyToManyField,
                models.ManyToManyRel
            ])):
                return True
            return False
        return list(filter(filter_fields, fields))

    def get_model_relation_through(self, field):
        if isinstance(field, models.ManyToManyRel):
            return self.serialize_model(field.through)
        elif isinstance(field, models.ManyToManyField):
            return self.serialize_model(field.remote_field.through)

    def get_display_model_fields(self):
        fields = self.get_model_fields()
        def filter_fields(x):
            if x.name == self.ordering_field:
                return True
            elif self.fields:
                return x.name in self.fields
            return True
        return filter(filter_fields, fields)

    def serialize(self):
        return {
            'model': self.content_type.model,
            'app_label': self.content_type.app_label,
            'db_table': self.model._meta.db_table,
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,
            'hidden': self.hidden,
            'fields': map(lambda field: {
                'name': field.name,
                'db_column': field.get_attname_column()[1],
                'verbose_name': field.verbose_name,
                'is_relation': field.is_relation,
                'field': field.__class__.__name__,
                'editable': field.editable,
                'filterable': field.name in self.filter_class.Meta.fields,
                'params': {
                    'related_model': self.serialize_model(field.related_model)
                }
            }, self.get_display_model_fields()),
            'flex_fields': [],
            'relations': map(lambda field: {
                'name': field.name,
                'verbose_name': field.related_model._meta.verbose_name_plural,
                'related_model': self.serialize_model(field.related_model),
                'field': field.__class__.__name__,
                'related_model_field': field.remote_field.name,
                'through': self.get_model_relation_through(field)
            }, self.get_model_relations()),
            'actions': map(lambda action: {
                'name': action._meta.name,
                'verbose_name': action._meta.verbose_name,
                'fields': map(lambda field: {
                    'name': field[0],
                    'verbose_name': field[1].label or field[0],
                    'related_model': self.serialize_model(field[1].queryset.model) if hasattr(field[1], 'queryset') else None,
                    'field': field[1].__class__.__name__
                }, action.get_fields().items()),
            }, map(lambda action: action(), self.actions)),
            'ordering_field': self.ordering_field
        }

    def get_model(self):
        return {
            'model': self.content_type.model,
            'app_label': self.content_type.app_label,
        }

    def get_related_models(self):
        return map(lambda field: {
            'model': field.related_model,
            'model_info': self.serialize_model(field.related_model)
        }, self.get_model_relations())

    def serialize_model(self, Model):
        if not Model:
            return
        content_type = ContentType.objects.get_for_model(Model)
        return {
            'model': content_type.model,
            'app_label': content_type.app_label
        }
