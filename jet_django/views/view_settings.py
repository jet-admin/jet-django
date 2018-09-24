from django.http import Http404
from django.shortcuts import get_object_or_404
from jet_django.deps.rest_framework import viewsets

from jet_django.filters.view_settings import ViewSettingsFilterSet
from jet_django.models.view_settings import ViewSettings
from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.view_settings import ViewSettingsSerializer


class ViewSettingsViewSet(viewsets.ModelViewSet):
    model = ViewSettings
    serializer_class = ViewSettingsSerializer
    queryset = ViewSettings.objects
    filter_class = ViewSettingsFilterSet
    pagination_class = None
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def create(self, request, *args, **kwargs):
        try:
            object = self.get_object()
            return super().update(request, *args, **kwargs)
        except Http404:
            return super().create(request, *args, **kwargs)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {
            'app_label': self.request.data.get('app_label'),
            'model': self.request.data.get('model'),
            'view': self.request.data.get('view')
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
