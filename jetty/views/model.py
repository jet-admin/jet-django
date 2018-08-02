from django.core.exceptions import NON_FIELD_ERRORS
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from jetty.filters.model_group import GroupFilter
from jetty.pagination import CustomPageNumberPagination
from jetty.permissions import HasProjectPermissions
from jetty.serializers.reorder import reorder_serializer_factory


class GroupSerializer(serializers.Serializer):
    group = serializers.CharField()
    y_func = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        if 'group_serializer' in kwargs:
            self.fields['group'] = kwargs.pop('group_serializer')

        if 'y_func_serializer' in kwargs:
            self.fields['y_func'] = kwargs.pop('y_func_serializer')

        super().__init__(*args, **kwargs)


def model_viewset_factory(build_model, build_filter_class, build_serializer_class, build_detail_serializer_class, build_queryset, build_actions, ordering_field):
    ReorderSerializer = reorder_serializer_factory(build_queryset, ordering_field)

    class Viewset(viewsets.ModelViewSet):
        model = build_model
        queryset = build_queryset
        pagination_class = CustomPageNumberPagination
        filter_class = build_filter_class
        permission_classes = (HasProjectPermissions,)

        def get_serializer_class(self):
            if self.action == 'group':
                return GroupSerializer
            elif self.action == 'retrieve':
                return build_detail_serializer_class
            else:
                return build_serializer_class

        @list_route(methods=['get'])
        def group(self, request):
            queryset = self.filter_queryset(self.get_queryset())

            x_column = request.GET['_x_column']
            y_func = request.GET['_y_func']
            y_column = request.GET.get('_y_column', 'id')

            x_field = self.model._meta.get_field(x_column)
            y_field = self.model._meta.get_field(y_column)

            x_serializer = ModelSerializer.serializer_field_mapping[type(x_field)]()
            y_serializer = ModelSerializer.serializer_field_mapping[type(y_field)]()

            queryset = GroupFilter().filter(queryset, {
                'x_column': x_column,
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
            # print(2, args, kwargs)
            return serializer_class(*args, **kwargs)

        @list_route(methods=['post'])
        def reorder(self, request):
            serializer = ReorderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        @list_route(methods=['post'])
        def reset_order(self, request):
            i = 1
            for instance in build_queryset:
                setattr(instance, ordering_field, i)
                instance.save()
                i += 1
            return Response({})

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
