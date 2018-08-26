from rest_framework import viewsets

from jet_django.filters.widget import WidgetFilterSet
from jet_django.models.widget import Widget
from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.widget_detail import WidgetDetailSerializer


class WidgetViewSet(viewsets.ModelViewSet):
    model = Widget
    serializer_class = WidgetDetailSerializer
    queryset = Widget.objects.prefetch_related('dashboard').all()
    filter_class = WidgetFilterSet
    pagination_class = None
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)
