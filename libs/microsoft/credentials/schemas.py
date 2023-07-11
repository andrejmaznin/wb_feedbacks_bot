from typing import Mapping, Optional

from pydantic import BaseModel

from libs.ydb import prepare_and_execute_query


class MSAdminCredentials(BaseModel):
    id: str
    ms_access_token: str
    ms_refresh_token: str

    @classmethod
    def parse_row(cls, row: Mapping) -> Optional['AdminCredentialsSchema']:
        if not all([hasattr(row, 'id'), hasattr(row, 'ms_access_token'), hasattr(row, 'ms_refresh_token')]):
            return None

        result = cls(
            id=row.id.decode('utf-8'),
            ms_access_token=row.ms_access_token.decode('utf-8'),
            ms_refresh_token=row.ms_refresh_token.decode('utf-8'),
        )
        return result

    @classmethod
    def get_by_id(cls, id_: str) -> Optional['AdminCredentialsSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $credentialId AS String;'
            'SELECT id, ms_access_token, ms_refresh_token FROM admin_credentials '
            'WHERE id=$credentialId',
            credentialId=id_
        )
        return cls.parse_row(rows[0]) if rows else None

    def upsert(self) -> None:
        prepare_and_execute_query(
            'DECLARE $credentialId AS String;'
            'DECLARE $MSAccessToken AS String;'
            'DECLARE $MSRefreshToken AS String;'
            'UPSERT INTO admin_credentials (id, created_at, ms_access_token, ms_refresh_token) '
            'VALUES ($credentialId, CurrentUTCTimestamp(), $MSAccessToken, $MSRefreshToken)',
            credentialId=self.id,
            MSAccessToken=self.ms_access_token,
            MSRefreshToken=self.ms_refresh_token
        )

    def fetch(self) -> 'AdminCredentialsSchema':
        rows = prepare_and_execute_query(
            'DECLARE $credentialId AS String;'
            'SELECT id, ms_access_token, ms_refresh_token FROM admin_credentials '
            'WHERE id=$credentialId',
            credentialId=self.id
        )
        return self.parse_row(rows[0])

    def update_tokens(self, new_access_token: str, new_refresh_token: str) -> 'AdminCredentialsSchema':
        self.ms_access_token = new_access_token
        self.ms_refresh_token = new_refresh_token
        self.upsert()
        return self.fetch()
