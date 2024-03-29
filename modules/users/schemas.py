from typing import List, Mapping, Optional, Union

from pydantic import BaseModel

from libs.ydb import prepare_and_execute_query


class UserSchema(BaseModel):
    id: str
    client_id: str
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    data: Optional[str] = None
    pending: bool = False
    owner: Optional[bool] = None

    @classmethod
    def parse_rows(cls, rows: List[Mapping]) -> List['UserSchema']:
        results = []
        for row in rows:
            if user := cls.parse_row(row):
                results.append(user)
        return results

    @classmethod
    def parse_row(cls, row: Mapping) -> Optional['UserSchema']:
        if not all([hasattr(row, 'id'), hasattr(row, 'client_id')]):
            return None

        result = cls(
            id=row.id.decode('utf-8'),
            client_id=row.client_id.decode('utf-8'),
        )
        if hasattr(row, 'telegram_id') and row.telegram_id is not None:
            result.telegram_id = int(row.telegram_id.decode('utf-8'))
        if hasattr(row, 'username') and row.username is not None:
            result.username = row.username.decode('utf-8')
        if hasattr(row, 'data') and row.data is not None:
            result.data = row.data.decode('utf-8')
        if hasattr(row, 'pending'):
            result.pending = row.pending
        if hasattr(row, 'owner'):
            result.owner = row.owner
        return result

    @classmethod
    def get_for_client(cls, client_id: str) -> List['UserSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, telegram_id, username, data, pending, owner FROM users '
            'WHERE client_id=$clientId',
            clientId=client_id
        )
        return cls.parse_rows(rows)

    @classmethod
    def get_by_telegram_id(cls, telegram_id: Union[str, int]) -> Optional['UserSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $telegramId AS String;'
            'SELECT id, client_id, telegram_id, username, data, pending, owner FROM users '
            'WHERE telegram_id = $telegramId',
            telegramId=str(telegram_id)
        )
        if rows:
            return cls.parse_row(rows[0])
        return None
