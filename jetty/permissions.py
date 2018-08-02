from rest_framework.permissions import BasePermission

from jetty.utils.backend import project_auth


class HasProjectPermissions(BasePermission):
    token_prefix = 'Token '

    def has_permission(self, request, view):
        print('check', request.META)

        token = request.META['HTTP_AUTHORIZATION']

        if token[:len(self.token_prefix)] != self.token_prefix:
            return False

        token = token[len(self.token_prefix):]

        return project_auth(token)
