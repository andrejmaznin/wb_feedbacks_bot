import logging
import time

from app.connections import get_redis_client
from libs.microsoft.auth import MSAuthClient
from libs.microsoft.credentials import MSAdminCredentials

logger = logging.getLogger(__name__)


def get_token(auth_code: str) -> None:
    ms_auth_client = MSAuthClient()

    access_token, refresh_token = ms_auth_client.get_tokens(auth_code=auth_code)
    credentials = MSAdminCredentials(id='andrew', ms_access_token=access_token, ms_refresh_token=refresh_token)
    credentials.upsert()


def refresh_ms_token() -> None:
    redis_client = get_redis_client()

    if redis_client.get('microsoft:refresh-tokens'):
        while redis_client.get('microsoft:refresh'):
            time.sleep(0.1)
        return

    redis_client.set('microsoft:refresh-tokens', 'True', ex=60)

    ms_auth_client = MSAuthClient()

    credentials = MSAdminCredentials.get_by_id(id_='andrew')
    new_access_token, new_refresh_token = ms_auth_client.refresh_tokens(refresh_token=credentials.ms_refresh_token)

    credentials.ms_access_token = new_access_token
    credentials.ms_refresh_token = new_refresh_token
    credentials.upsert()

    redis_client.delete('microsoft:refresh-tokens')
