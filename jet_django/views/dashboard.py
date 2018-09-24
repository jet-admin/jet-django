from jet_django.deps.rest_framework import viewsets
from jet_django.deps.rest_framework.decorators import detail_route
from jet_django.deps.rest_framework.response import Response

from jet_django.models.dashboard import Dashboard
from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.dashboard import DashboardSerializer
from jet_django.serializers.dashboard_set_widgets import DashboardSetWidgetsSerializer


class DashboardViewSet(viewsets.ModelViewSet):
    model = Dashboard
    serializer_class = DashboardSerializer
    queryset = Dashboard.objects.prefetch_related('widgets').all()
    pagination_class = None
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    @detail_route(methods=['put'])
    def set_widgets(self, request, *args, **kwargs):
        serializer = DashboardSetWidgetsSerializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        instance_serializer = self.get_serializer(instance=self.get_object())

        return Response(instance_serializer.data)
