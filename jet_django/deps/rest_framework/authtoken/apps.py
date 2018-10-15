from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthTokenConfig(AppConfig):
    name = 'jet_django.deps.rest_framework.authtoken'
    verbose_name = _("Auth Token")
