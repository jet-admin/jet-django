from django.core.exceptions import NON_FIELD_ERRORS
from rest_framework import status, viewsets, pagination
from rest_framework.decorators import list_route
from rest_framework.response import Response

from jetty.serializers.reorder import reorder_serializer_factory


def model_viewset_factory(build_model, build_filter_class, build_serializer_class, build_detail_serializer_class, build_queryset, build_actions, ordering_field):
    ReorderSerializer = reorder_serializer_factory(build_queryset, ordering_field)

    class Viewset(viewsets.ModelViewSet):
        model = build_model
        queryset = build_queryset
        # permission_classes = [permissions.DjangoModelPermissions]
        pagination_class = pagination.PageNumberPagination
        filter_class = build_filter_class

        def get_serializer_class(self):
            if self.action == 'retrieve':
                return build_detail_serializer_class
            else:
                return build_serializer_class

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
