from jet_django.deps.rest_framework import views
from jet_django.deps.rest_framework.response import Response
from jet_django.admin.jet import jet
from jet_django.mixins.cors_api_view import CORSAPIViewMixin
from jet_django.permissions import HasProjectPermissions


class ModelDescriptionView(CORSAPIViewMixin, views.APIView):
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def get(self, request, *args, **kwargs):
        return Response(map(lambda x: x.serialize(), jet.models))
