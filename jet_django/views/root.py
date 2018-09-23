from rest_framework import views
from rest_framework.response import Response

from jet_django import VERSION


class RootView(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            'version': VERSION
        })
