from django.core.management import BaseCommand

from jet_django.utils.backend import get_token


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('token', nargs='?', type=str)

    def handle(self, *args, **options):
        token = get_token()

        if token:
            print('Jet Admin Token:')
            print(token)
        else:
            print('Jet Admin Token is not set')
