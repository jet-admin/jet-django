from django.apps import AppConfig
from django.apps import apps


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

        try:
            register_token()
        except:  # if no migrations yet
            pass
