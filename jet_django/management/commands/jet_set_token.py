import uuid

from django.core.management import BaseCommand
from django.utils import timezone

from jet_django.models.token import Token


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('token', nargs='?', type=str)

    def handle(self, *args, **options):
        token = uuid.UUID(options.get('token'))

        if not token:
            print('No token was specified')
            return

        project_token = Token.objects.all().first()

        if project_token:
            if project_token.token == token:
                print('This token is already set, ignoring')
                return

            project_token.token = token
            project_token.date_add = timezone.now()
            project_token.save()
            print('Token changed to {}'.format(project_token.token))
        else:
            project_token = Token.objects.create(token=token, date_add=timezone.now())
            print('Token created {}'.format(project_token.token))
