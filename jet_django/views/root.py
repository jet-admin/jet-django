from jet_django.deps.rest_framework import views
from jet_django.deps.rest_framework.response import Response

from jet_django import VERSION


class RootView(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            'version': VERSION
        })
