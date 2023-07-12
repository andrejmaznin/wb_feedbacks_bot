import logging
import time
from typing import Optional

import requests

from libs.microsoft.auth.decorator import handle_refresh_token
from libs.microsoft.auth.exceptions import MSAuthException

logger = logging.getLogger(__name__)


class MSWebAPIClient:
    base_url: str = 'https://graph.microsoft.com/v1.0'
    access_token: str
    refresh_token: str

    def __init__(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token

    @property
    def authorization_headers(self):
        return {'Authorization': f'Bearer {self.access_token}'}

    @handle_refresh_token
    def get_item(self, item_id: str) -> dict:
        response = requests.get(
            url=self.base_url + f'/me/drive/items/{item_id}',
            headers=self.authorization_headers
        )
        if 400 <= response.status_code < 500:
            print('Error while getting item', response.text)
            raise MSAuthException

        return response.json()

    @handle_refresh_token
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
        if 400 <= response.status_code < 500:
            print(f'Error while copying item {response.text}')
            raise MSAuthException

        monitor_url = response.headers.get('Location')

        print(monitor_url)
        while True:
            response = requests.get(url=monitor_url)
            data = response.json()
            if data.get('status') == 'completed':
                return data.get('resourceId')
            time.sleep(0.2)

    @handle_refresh_token
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
        if 400 <= response.status_code < 500:
            raise MSAuthException

        data = response.json()
        return data['link']['webUrl']

    @handle_refresh_token
    def download_item_content(self, item_id: str) -> Optional[bytes]:
        response = requests.get(
            url=self.base_url + f'/me/drive/items/{item_id}/content',
            headers=self.authorization_headers
        )
        if 400 <= response.status_code < 500:
            raise MSAuthException

        return response.content

    @handle_refresh_token
    def delete_item(self, item_id: str) -> None:
        response = requests.delete(
            url=self.base_url + f'/me/drive/items/{item_id}',
            headers=self.authorization_headers
        )
        if 400 <= response.status_code < 500:
            print(response.text)
            data = response.json()
            if error := data.get('error'):
                if error_code := error.get('code'):
                    if 'accessDenied' in error_code or 'itemNotFound' in error_code:
                        return

            raise MSAuthException

    @handle_refresh_token
    def get_children(self, path: str) -> list[dict]:
        response = requests.get(
            url=self.base_url + f'/me/drive/{path}',
            headers=self.authorization_headers
        )
        if 400 <= response.status_code < 500:
            print(response.text)
            raise MSAuthException

        return response.json()
