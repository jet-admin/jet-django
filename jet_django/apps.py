import logging

import sys
from django.apps import AppConfig
from django.apps import apps

from jet_django import settings

logger = logging.getLogger('jet_django')


class JetDjangoConfig(AppConfig):
    name = 'jet_django'

    def ready(self):
        from jet_django.utils.backend import register_token, is_token_activated
        from jet_django.admin.jet import jet

        try:
            models = apps.get_models()

            for model in models:
                jet.register(model)
        except:  # if no migrations yet
            pass

        is_command = len(sys.argv) > 1 and sys.argv[1].startswith('jet_')

        if not is_command and settings.JET_REGISTER_TOKEN_ON_START:
            try:
                print('[JET] Checking if token is not activated yet...')
                token, created = register_token()

                if not token:
                    return

                if not is_token_activated(token):
                    print('[!] Your server token is not activated')
                    print('[!] Token: {}'.format(token.token))
                else:
                    print('[JET] Token activated')
            except Exception as e:  # if no migrations yet
                print(e)
                pass
