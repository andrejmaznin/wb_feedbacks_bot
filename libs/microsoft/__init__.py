from libs.microsoft.clients import MSAPIClient
from libs.microsoft.clients import MSAuthClient
from libs.microsoft.credentials import MSAdminCredentials

credentials = None
client = None
auth_client = None


def get_ms_client():
    global client, credentials

    if client is None:
        credentials = MSAdminCredentials.initialize()
        client = MSAPIClient(token=credentials.access_token)
    return client


def get_ms_auth_client():
    global auth_client

    if auth_client is None:
        auth_client = MSAuthClient()
    return auth_client
