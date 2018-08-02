from django.apps import AppConfig
from django.db import ProgrammingError


class JettyConfig(AppConfig):
    name = 'jetty'

    def ready(self):
        from jetty.utils.backend import register_token

        try:
            register_token()
        except:  # if no migrations yet
            pass
