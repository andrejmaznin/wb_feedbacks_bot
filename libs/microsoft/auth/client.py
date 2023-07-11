import logging
from typing import Tuple

import requests

from app.settings import settings
from libs.microsoft.auth.exceptions import MSAuthException

logger = logging.getLogger(__name__)


class MSAuthClient:
    base_url: str = 'https://login.microsoftonline.com'

    def get_tokens(self, auth_code: str) -> Tuple[str, str]:
        form_data = {
            'code': auth_code,
            'client_id': settings.MICROSOFT.client_id,
            'client_secret': settings.MICROSOFT.client_secret,
            'scope': 'offline_access files.readwrite.all',
            'grant_type': 'authorization_code'
        }
        params = {'redirect_url': settings.MICROSOFT.redirect_url}

        response = requests.post(
            url=self.base_url + '/consumers/oauth2/v2.0/token',
            data=form_data,
            params=params
        )
        if response.status_code != 200:
            print(f'Error while getting tokens {response.text}')
            raise MSAuthException

        data = response.json()
        return data['access_token'], data['refresh_token']

    def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        form_data = {
            'refresh_token': refresh_token,
            'client_id': settings.MICROSOFT.client_id,
            'client_secret': settings.MICROSOFT.client_secret,
            'scope': 'offline_access files.readwrite.all',
            'grant_type': 'refresh_token'
        }
        response = requests.post(
            url=self.base_url + '/consumers/oauth2/v2.0/token',
            data=form_data
        )
        if response.status_code != 200:
            print(f'Error while refreshing tokens {response.text}')
            raise MSAuthException

        data = response.json()
        return data['access_token'], data['refresh_token']
