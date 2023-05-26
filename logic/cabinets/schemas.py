import logging
from functools import lru_cache
from typing import List, Mapping, Optional

from pydantic import BaseModel

from libs.ydb import get_or_generate_id, prepare_and_execute_query
from libs.ydb.utils import prepare_and_execute_query_async
from logic.cabinets.consts import WB_HEADERS

logger = logging.getLogger(__name__)


class CabinetSchema(BaseModel):
    id: str
    client_id: str
    title: str
    invalid: bool
    token: Optional[str] = None

    @property
    def headers(self):
        return {
            'Authorization': self.token,
            **WB_HEADERS
        }

    @classmethod
    def parse_rows(cls, rows: List[Mapping]) -> List['CabinetSchema']:
        results = []
        for row in rows:
            if cabinet := cls.parse_row(row):
                results.append(cabinet)
        return results

    @classmethod
    def parse_row(cls, row: Mapping) -> Optional['CabinetSchema']:
        if not all([
            hasattr(row, 'id'), hasattr(row, 'client_id'), hasattr(row, 'title'), hasattr(row, 'invalid')
        ]):
            return None
        if not all([row.id, row.client_id, row.title]):
            return None

        result = cls(
            id=row.id.decode('utf-8'),
            client_id=row.client_id.decode('utf-8'),
            title=row.title.decode('utf-8'),
            invalid=row.invalid or False
        )
        if hasattr(row, 'token') and row.token is not None:
            result.token = row.token.decode('utf-8')
        return result

    @classmethod
    def create(
        cls,
        client_id: str,
        title: str,
        token: str,
    ) -> 'CabinetSchema':
        cabinet_id = get_or_generate_id(
            'DECLARE $clientId AS String;'
            'DECLARE $title AS String;'
            'SELECT id FROM cabinets '
            'WHERE client_id=$clientId AND title=$title',
            clientId=client_id,
            title=title
        )
        prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'DECLARE $clientId AS String;'
            'DECLARE $title AS String;'
            'DECLARE $token AS String;'
            'UPSERT INTO cabinets (id, client_id, title, invalid, token) '
            'VALUES ($cabinetId, $clientId, $title, False, $token)',
            cabinetId=cabinet_id,
            clientId=client_id,
            title=title,
            token=token,
        )
        return cls.get_by_id(cabinet_id)

    @classmethod
    def get_by_id(cls, id: str) -> Optional['CabinetSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'SELECT id, client_id, title, invalid, token FROM cabinets WHERE id=$cabinetId',
            cabinetId=id
        )
        return cls.parse_row(rows[0]) if rows else None

    @classmethod
    def get_for_client(cls, client_id: str) -> List['CabinetSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, title, invalid, token FROM cabinets '
            'WHERE client_id=$clientId',
            clientId=client_id
        )
        return cls.parse_rows(rows)

    def delete(self) -> None:
        prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'DELETE FROM cabinets '
            'WHERE id=$cabinetId;',
            cabinetId=self.id
        )

    @classmethod
    def delete_by_id(cls, id: str) -> None:
        prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'DELETE FROM cabinets WHERE id=$cabinetId',
            cabinetId=id
        )

    def mark_as_invalid(self) -> None:
        prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'UPSERT INTO cabinets (id, invalid) VALUES ($cabinetId, True);',
            cabinetId=self.id
        )

    async def mark_as_invalid_async(self) -> None:
        await prepare_and_execute_query_async(
            'DECLARE $cabinetId AS String;'
            'UPSERT INTO cabinets (id, invalid) VALUES ($cabinetId, True);',
            cabinetId=self.id
        )
