import logging
import requests

from jet_django import settings
from jet_django.models.token import Token

logger = logging.getLogger('jet_django')


def api_method_url(method):
    return '{}/{}'.format(settings.JET_BACKEND_API_BASE_URL, method)


def get_token():
    token = Token.objects.all().first()
    return token.token if token else None


def register_token():
    token = Token.objects.all().first()

    if token:
        logger.info('[JET] Token already registered')
        return token, False

    url = api_method_url('project_tokens/')
    headers = {
        'User-Agent': 'Jet Django'
    }

    r = requests.request('POST', url, headers=headers)
    success = 200 <= r.status_code < 300

    if not success:
        logger.error('[JET] Register Token request error: %s %s %s', r.status_code, r.reason, r.text)
        return None, False

    result = r.json()
    token = Token.objects.create(token=result['token'], date_add=result['date_add'])

    return token, True


def is_token_activated(token):
    url = api_method_url('project_tokens/{}/'.format(token.token))
    headers = {
        'User-Agent': 'Jet Django'
    }

    r = requests.request('GET', url, headers=headers)
    success = 200 <= r.status_code < 300

    if not success:
        return False

    result = r.json()

    return result.get('activated') is True


def reset_token():
    Token.objects.all().delete()

    return register_token()


def project_auth(token, permission=None):
    project_token = Token.objects.all().first()

    if not project_token:
        logger.error('[JET] Project Auth request error: not token registered')
        return {
            'result': False
        }

    url = api_method_url('project_auth/')
    data = {
        'project_token': project_token.token,
        'token': token
    }
    headers = {
        'User-Agent': 'Jet Django'
    }

    if permission:
        data.update(permission)

    r = requests.request('POST', url, data=data, headers=headers)
    success = 200 <= r.status_code < 300

    if not success:
        logger.error('[JET] Project Auth request error: %s %s %s', r.status_code, r.reason, r.text)
        return {
            'result': False
        }

    result = r.json()

    if result.get('access_disabled'):
        logger.error('[JET] Project Auth request error: access_disabled')
        return {
            'result': False,
            'warning': result.get('warning')
        }

    return {
        'result': True,
        'warning': result.get('warning')
    }
