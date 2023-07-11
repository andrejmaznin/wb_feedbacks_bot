from libs.microsoft.auth.client import MSAuthClient
from libs.microsoft.auth.internals import get_token

auth_client = None


def get_ms_auth_client():
    global auth_client

    if auth_client is None:
        auth_client = MSAuthClient()
    return auth_client
