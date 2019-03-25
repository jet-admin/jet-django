from django.core.exceptions import NON_FIELD_ERRORS

from jet_django.deps.rest_framework import status, viewsets, serializers
from jet_django.deps.rest_framework.decorators import list_route, detail_route
from jet_django.deps.rest_framework.generics import get_object_or_404
from jet_django.deps.rest_framework.response import Response
from jet_django.deps.rest_framework.serializers import ModelSerializer
from jet_django.filters.model_aggregate import AggregateFilter
from jet_django.filters.model_group import GroupFilter
from jet_django.mixins.cors_api_view import CORSAPIViewMixin
from jet_django.mixins.method_override import MethodOverrideViewMixin
from jet_django.pagination import CustomPageNumberPagination
from jet_django.permissions import HasProjectPermissions, ModifyNotInDemo
from jet_django.serializers.reorder import reorder_serializer_factory
from jet_django.serializers.reset_order import reset_order_serializer_factory
from jet_django.utils.siblings import get_model_siblings


class AggregateSerializer(serializers.Serializer):
    y_func = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        if 'y_func_serializer' in kwargs:
            self.fields['y_func'] = kwargs.pop('y_func_serializer')

        super().__init__(*args, **kwargs)


class GroupSerializer(serializers.Serializer):
    group = serializers.CharField()
    y_func = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        if 'group_serializer' in kwargs:
            self.fields['group'] = kwargs.pop('group_serializer')

        if 'y_func_serializer' in kwargs:
            self.fields['y_func'] = kwargs.pop('y_func_serializer')

        super().__init__(*args, **kwargs)


def model_viewset_factory(build_model, build_filter_class, build_serializer_class, build_detail_serializer_class, build_queryset, build_actions):
    ReorderSerializer = reorder_serializer_factory(build_queryset)
    ResetOrderSerializer = reset_order_serializer_factory(build_queryset)

    class Viewset(MethodOverrideViewMixin, CORSAPIViewMixin, viewsets.ModelViewSet):
        model = build_model
        queryset = build_queryset
        pagination_class = CustomPageNumberPagination
        filter_class = build_filter_class
        authentication_classes = ()
        permission_classes = (HasProjectPermissions, ModifyNotInDemo)

        @property
        def required_project_permission(self):
            return {
                'permission_type': 'model',
                'permission_object': self.kwargs['model'],
                'permission_actions': {
                    'create': 'w',
                    'update': 'w',
                    'partial_update': 'w',
                    'destroy': 'd',
                    'retrieve': 'r',
                    'list': 'r',
                    'aggregate': 'r',
                    'group': 'r',
                    'reorder': 'w',
                    'reset_order': 'w'
                }.get(self.action, 'w')
            }

        def get_serializer_class(self):
            if self.action == 'aggregate':
                return AggregateSerializer
            elif self.action == 'group':
                return GroupSerializer
            elif self.action == 'retrieve':
                return build_detail_serializer_class
            else:
                return build_serializer_class

        @list_route(methods=['get'])
        def aggregate(self, request, *args, **kwargs):
            queryset = self.filter_queryset(self.get_queryset())

            y_func = request.GET['_y_func'].lower()
            y_column = request.GET.get('_y_column', 'id')

            y_field = self.model._meta.get_field(y_column)

            y_serializer_class, y_serializer_kwargs = ModelSerializer().build_standard_field(y_column, y_field)
            y_serializer = y_serializer_class(**y_serializer_kwargs)

            queryset = AggregateFilter().filter(queryset, {
                'y_func': y_func,
                'y_column': y_column
            })

            serializer = self.get_serializer(
                queryset,
                y_func_serializer=y_serializer
            )

            return Response(serializer.data)

        @list_route(methods=['get'])
        def group(self, request, *args, **kwargs):
            queryset = self.filter_queryset(self.get_queryset())

            x_column = request.GET['_x_column']
            x_lookup_name = request.GET.get('_x_lookup')
            y_func = request.GET['_y_func'].lower()
            y_column = request.GET.get('_y_column', 'id')

            x_field = self.model._meta.get_field(x_column)
            x_lookup = x_field.class_lookups.get(x_lookup_name)
            y_field = self.model._meta.get_field(y_column)

            if x_lookup:
                x_field = x_lookup('none').output_field

            x_serializer_class, x_serializer_kwargs = ModelSerializer().build_standard_field(x_column, x_field)
            x_serializer = x_serializer_class(**x_serializer_kwargs)

            y_serializer_class, y_serializer_kwargs = ModelSerializer().build_standard_field(y_column, y_field)
            y_serializer = y_serializer_class(**y_serializer_kwargs)

            queryset = GroupFilter().filter(queryset, {
                'x_column': x_column,
                'x_lookup': x_lookup,
                'y_func': y_func,
                'y_column': y_column
            })
            serializer = self.get_serializer(
                queryset,
                many=True,
                group_serializer=x_serializer,
                y_func_serializer=y_serializer
            )

            return Response(serializer.data)

        def get_serializer(self, *args, **kwargs):
            """
            Return the serializer instance that should be used for validating and
            deserializing input, and for serializing output.
            """
            serializer_class = self.get_serializer_class()
            kwargs['context'] = self.get_serializer_context()
            return serializer_class(*args, **kwargs)

        @list_route(methods=['post'])
        def reorder(self, request, *args, **kwargs):
            serializer = ReorderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        @list_route(methods=['post'])
        def reset_order(self, request, *args, **kwargs):
            serializer = ResetOrderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        def get_object(self):
            print('wtf')
            return super().get_object()

        @detail_route(methods=['get'])
        def get_siblings(self, request, *args, **kwargs):
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_object_or_404(self.get_queryset(), **filter_kwargs)

            # May raise a permission denied
            self.check_object_permissions(self.request, obj)

            queryset = self.filter_queryset(self.get_queryset())

            return Response(get_model_siblings(self.model, obj, queryset))

    for action in build_actions:
        def route(self, request):
            form = action(data=request.data)

            if not form.is_valid():
                return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

            queryset = form.filer_queryset(self.get_queryset())

            try:
                result = form.save(queryset)
            except Exception as e:
                return Response({NON_FIELD_ERRORS: str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'action': form._meta.name, 'result': result})

        decorator = list_route(methods=['post'])
        route = decorator(route)

        setattr(Viewset, action._meta.name, route)

    return Viewset
