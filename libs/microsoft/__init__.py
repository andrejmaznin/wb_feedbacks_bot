from libs.microsoft.auth import get_ms_auth_client
from libs.microsoft.client import MSWebAPIClient
from libs.microsoft.credentials import get_credentials

client = None


def get_ms_client():
    global client

    if client is None:
        ms_credentials = get_credentials()
        client = MSWebAPIClient(
            access_token=ms_credentials.ms_access_token,
            refresh_token=ms_credentials.ms_refresh_token
        )
    return client
