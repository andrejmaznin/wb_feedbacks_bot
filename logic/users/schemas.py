from typing import Optional, List, Mapping

from pydantic import BaseModel


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
        if not hasattr(row, 'id') and hasattr(row, 'client_id'):
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
