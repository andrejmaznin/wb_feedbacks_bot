import logging
import time
from typing import Optional, Tuple

import requests

from app.settings import settings
from libs.microsoft.exceptions import MSAuthException

logger = logging.getLogger(__name__)


class MSAPIClient:
    base_url: str = 'https://graph.microsoft.com/v1.0'
    token: str

    def __init__(self, token: str):
        self.token = token

    @property
    def authorization_headers(self):
        return {'Authorization': f'Bearer {self.token}'}

    def get_item(self, item_id) -> dict:
        response = requests.get(
            url=self.base_url + f'/me/drive/items/{item_id}',
            headers=self.authorization_headers
        )
        if not 200 <= response.status_code < 300:
            logger.error('Error while getting item', response.text)
            return

        return response.json()

    def copy_item(self, item_id: str, parent_reference: dict, name: str) -> Optional[str]:
        body = {
            'parentReference': parent_reference,
            'name': name,
        }
        response = requests.post(
            url=self.base_url + f'/me/drive/items/{item_id}/copy',
            headers=self.authorization_headers,
            json=body
        )
        if not 200 <= response.status_code < 300:
            logger.error('Error while copying item', response.text)
            return

        while True:
            response = requests.get(
                url=self.base_url + f'/me/drive/items/{parent_reference["id"]}/children',
                headers=self.authorization_headers
            )
            if not 200 <= response.status_code < 300:
                logger.error('Error while scanning', response.text)
                return

            data = response.json()
            for item in data['value']:
                if item['name'] == name:
                    return item['id']
            time.sleep(0.2)

    def create_url_for_item(self, item_id: str, url_type: str, scope: str) -> Optional[str]:
        body = {
            'type': url_type,
            'scope': scope
        }
        response = requests.post(
            url=self.base_url + f'/me/drive/items/{item_id}/createLink',
            headers=self.authorization_headers,
            json=body
        )
        if not 200 <= response.status_code < 300:
            logger.error('Error while creating url', response.text)
            return
        data = response.json()
        return data['link']['webUrl']

    def download_item_content(self, item_id: str) -> Optional[bytes]:
        response = requests.get(
            url=self.base_url + f'/me/drive/items/{item_id}/content',
            headers=self.authorization_headers
        )
        if not 200 <= response.status_code < 300:
            logger.error('Error while downloading item', response.text)
            return
        return response.content

    def delete_item(self, item_id: str) -> None:
        response = requests.delete(
            url=self.base_url + f'/me/drive/items/{item_id}',
            headers=self.authorization_headers
        )
        if not 200 <= response.status_code < 300:
            logger.error('Error while deleting item', response.text)
            return


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
            logger.error('Error while getting tokens', response.text)
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
            logger.error('Error while refreshing token', response.text)
            raise MSAuthException

        data = response.json()
        return data['access_token'], data['refresh_token']
