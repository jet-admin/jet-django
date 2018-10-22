from jet_django.deps.rest_framework import views
from jet_django.deps.rest_framework.response import Response
from jet_django.mixins.cors_api_view import CORSAPIViewMixin
from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.sql import SqlSerializer


class SqlView(CORSAPIViewMixin, views.APIView):
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def post(self, request, *args, **kwargs):
        serializer = SqlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.execute())
