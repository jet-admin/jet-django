from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from jetty.models.dashboard import Dashboard
from jetty.serializers.dashboard import DashboardSerializer
from jetty.serializers.dashboard_set_widgets import DashboardSetWidgetsSerializer


class DashboardViewSet(viewsets.ModelViewSet):
    model = Dashboard
    serializer_class = DashboardSerializer
    queryset = Dashboard.objects.prefetch_related('widgets')
    pagination_class = None

    @detail_route(methods=['put'])
    def set_widgets(self, request, *args, **kwargs):
        serializer = DashboardSetWidgetsSerializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        instance_serializer = self.get_serializer(instance=self.get_object())

        return Response(instance_serializer.data)
