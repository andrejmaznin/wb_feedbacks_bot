from libs.microsoft.client import MicrosoftAPIClient
from libs.microsoft.credentials import MSAdminCredentials

credentials = None
microsoft_client = None


def get_microsoft_client():
    global microsoft_client

    if microsoft_client is None:
        credentials = MSAdminCredentials.initialize()
        microsoft_client = MicrosoftAPIClient(token=credentials.access_token)

    return microsoft_client

