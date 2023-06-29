import logging

from libs.microsoft import get_ms_auth_client
from modules.microsoft.schemas import AdminCredentialsSchema

logger = logging.getLogger(__name__)


def get_token(auth_code: str) -> None:
    ms_auth_client = get_ms_auth_client()

    access_token, refresh_token = ms_auth_client.get_tokens(auth_code=auth_code)
    credentials = AdminCredentialsSchema(id='andrew', ms_access_token=access_token, ms_refresh_token=refresh_token)
    credentials.upsert()


def refresh_ms_token() -> None:
    ms_auth_client = get_ms_auth_client()

    credentials = AdminCredentialsSchema.get_by_id(id_='andrew')
    new_access_token, new_refresh_token = ms_auth_client.refresh_tokens(refresh_token=credentials.ms_refresh_token)
    credentials.update_tokens(
        new_access_token=new_access_token,
        new_refresh_token=new_refresh_token
    )
