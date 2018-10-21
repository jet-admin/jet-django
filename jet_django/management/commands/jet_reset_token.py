from django.core.management import BaseCommand

from jet_django.utils.backend import reset_token


class Command(BaseCommand):
    def handle(self, *args, **options):
        token, created = reset_token()

        print('Token reset')

        if not created and token:
            print('Token already exists: {}'.format(token.token))
        elif not created and not token:
            print('Token creation failed')
        elif created and token:
            print('Token created: {}'.format(token.token))
