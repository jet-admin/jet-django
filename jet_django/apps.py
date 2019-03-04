import logging
from django.apps import AppConfig
from django.apps import apps

from jet_django import settings

logger = logging.getLogger('jet_django')


class JetDjangoConfig(AppConfig):
    name = 'jet_django'

    def ready(self):
        from jet_django.utils.backend import register_token
        from jet_django.admin.jet import jet

        try:
            models = apps.get_models()

            for model in models:
                jet.register(model)
        except:  # if no migrations yet
            pass

        if settings.JET_REGISTER_TOKEN_ON_START:
            try:
                logger.info('[JET] Checking if token is not registered yet...')
                register_token()
            except:  # if no migrations yet
                pass
