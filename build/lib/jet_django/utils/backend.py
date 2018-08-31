import requests

from jet_django import settings
from jet_django.models.token import Token


def api_method_url(method):
    return '{}/{}'.format(settings.JET_BACKEND_API_BASE_URL, method)


def register_token():
    token = Token.objects.all().first()

    if token:
        return token, False

    url = api_method_url('project_tokens/')
    headers = {
        'User-Agent': 'Jet Django'
    }

    r = requests.request('POST', url, headers=headers)
    success = 200 <= r.status_code < 300

    if not success:
        print('Register Token request error', r.status_code, r.reason)
        return None, False

    result = r.json()
    token = Token.objects.create(token=result['token'], date_add=result['date_add'])

    return token, True


def project_auth(token):
    project_token = Token.objects.all().first()

    if not project_token:
        return False

    url = api_method_url('project_auth/')
    data = {
        'project_token': project_token.token,
        'token': token
    }
    headers = {
        'User-Agent': 'Jet Django'
    }

    r = requests.request('POST', url, data=data, headers=headers)
    success = 200 <= r.status_code < 300

    if not success:
        print('Project Auth request error', r.status_code, r.reason)
        return False

    return True
