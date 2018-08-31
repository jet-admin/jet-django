from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from jet_django.models.menu_item import MenuSettings
from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.menu_settings import MenuSettingsSerializer


class MenuSettingsViewSet(viewsets.ModelViewSet):
    model = MenuSettings
    serializer_class = MenuSettingsSerializer
    queryset = MenuSettings.objects.all()
    pagination_class = None
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def create(self, request, *args, **kwargs):
        try:
            self.get_object()
            return super().update(request, *args, **kwargs)
        except Http404:
            return super().create(request, *args, **kwargs)

    def get_object(self):
        queryset = self.get_queryset()[:1]
        obj = get_object_or_404(queryset)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
