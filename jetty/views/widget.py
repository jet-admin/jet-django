from rest_framework import viewsets

from jetty.filters.widget import FilterSet
from jetty.models.widget import Widget
from jetty.serializers.widget_detail import WidgetDetailSerializer


class WidgetViewSet(viewsets.ModelViewSet):
    model = Widget
    serializer_class = WidgetDetailSerializer
    queryset = Widget.objects.prefetch_related('dashboard')
    filter_class = FilterSet
    pagination_class = None
