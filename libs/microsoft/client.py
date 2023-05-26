import time
from typing import Optional

import requests


class MicrosoftAPIClient:
    base_url: str = 'https://graph.microsoft.com/v1.0'
    token: str

    def __init__(self, token: str):
        self.token = token

    @property
    def authorization_headers(self):
        return {'Authorization': f'Bearer {self.token}'}

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
            return

        while True:
            response = requests.get(
                url=self.base_url + f'/me/drive/items/{parent_reference["id"]}/children',
                headers=self.authorization_headers
            )
            if not 200 <= response.status_code < 300:
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
            return
        data = response.json()
        return data['link']['webUrl']

    def download_item_content(self, item_id: str) -> Optional[bytes]:
        response = requests.get(
            url=self.base_url + f'/me/drive/items/{item_id}/content',
            headers=self.authorization_headers
        )
        if not 200 <= response.status_code < 300:
            return
        return response.content
