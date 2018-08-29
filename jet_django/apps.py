from django.apps import AppConfig


class JetDjangoConfig(AppConfig):
    name = 'jet_django'

    def ready(self):
        from jet_django.utils.backend import register_token

        try:
            register_token()
        except:  # if no migrations yet
            pass
