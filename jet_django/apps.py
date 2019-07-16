import logging

import sys
from django.apps import AppConfig
from django.apps import apps
from django.db import ProgrammingError

from jet_django import settings

logger = logging.getLogger('jet_django')


class JetDjangoConfig(AppConfig):
    name = 'jet_django'

    def check_token(self):
        from jet_django.utils.backend import register_token, is_token_activated

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
            except ProgrammingError as e:
                no_migrations = str(e).find('relation "jet_django_token" does not exist') != -1
                if no_migrations:
                    print('[JET] Apply migrations first: python manage.py migrate jet_django')
                else:
                    print(e)
            except Exception as e:  # if no migrations yet
                print(e)
                pass

    def register_models(self):
        from jet_django.admin.jet import jet

        try:
            models = apps.get_models()

            for model in models:
                jet.register(model)
        except:  # if no migrations yet
            pass

    def ready(self):
        self.check_token()
        self.register_models()
