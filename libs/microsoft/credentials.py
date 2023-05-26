from libs.ydb import prepare_and_execute_query


class MSAdminCredentials:
    id: str
    access_token: str
    refresh_token: str

    @classmethod
    def initialize(cls):
        rows = prepare_and_execute_query(
            'DECLARE $credentialId AS String;'
            'SELECT id, access_token, refresh_token FROM admin_credentials WHERE id=$credentialId',
            credetialId='andrew'
        )
        creds = cls()
        creds.id = rows[0].id.decode('utf-8')
        creds.access_token = rows[0].access_token.decode('utf-8')
        creds.refresh_token = rows[0].refresh_token.decode('utf-8')
        return creds
