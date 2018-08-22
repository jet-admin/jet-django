from rest_framework.permissions import BasePermission

from jetty import settings
from jetty.utils.backend import project_auth


class HasProjectPermissions(BasePermission):
    token_prefixes = ['Token ', 'ProjectToken ']

    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')

        if not token:
            return False

        return any(map(lambda x: token[:len(x)] == x and project_auth(token[len(x):]), self.token_prefixes))


class ModifyNotInDemo(BasePermission):

    def has_permission(self, request, view):
        if not settings.JETTY_DEMO:
            return True
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return False
        return True
