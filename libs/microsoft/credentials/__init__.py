from libs.microsoft.credentials.schemas import MSAdminCredentials

credentials = None


def initialize_credentials() -> MSAdminCredentials:
    global credentials
    credentials = MSAdminCredentials.get_by_id(id_='andrew')
    return credentials


def get_credentials() -> MSAdminCredentials:
    global credentials

    if credentials is None:
        credentials = MSAdminCredentials.get_by_id(id_='andrew')

    return credentials
