from libs.microsoft.auth.exceptions import MSAuthException
from libs.microsoft.auth.internals import refresh_ms_token
from libs.microsoft.credentials import initialize_credentials


def handle_refresh_token(func):
    def wrapper(web_client, *args, **kwargs):
        try:
            return func(web_client, *args, **kwargs)
        except MSAuthException:
            refresh_ms_token()
            new_credentials = initialize_credentials()

            web_client.access_token = new_credentials.ms_access_token
            web_client.refresh_token = new_credentials.ms_refresh_token

            return func(web_client, *args, **kwargs)

    return wrapper
