import logging
from datetime import datetime
from typing import List, Mapping, Optional

from pydantic import BaseModel

from libs.ydb import get_or_generate_id, prepare_and_execute_query
from libs.ydb.utils import prepare_and_execute_query_async

logger = logging.getLogger(__name__)


class CabinetSchema(BaseModel):
    id: str
    client_id: str
    created_at: datetime
    title: str
    invalid: bool
    table_url: Optional[str] = None
    table_id: Optional[str] = None
    token: Optional[str] = None

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
            hasattr(row, 'id'), hasattr(row, 'client_id'), hasattr(row, 'created_at'),
            hasattr(row, 'title'), hasattr(row, 'invalid')
        ]):
            return None
        if not all([row.id, row.client_id, row.created_at, row.title]):
            return None

        result = cls(
            id=row.id.decode('utf-8'),
            client_id=row.client_id.decode('utf-8'),
            created_at=row.created_at,
            title=row.title.decode('utf-8'),
            invalid=row.invalid or False,
        )

        # fields that might not be needed in logic
        if hasattr(row, 'token') and row.token is not None:
            result.token = row.token.decode('utf-8')
        if hasattr(row, 'table_id') and row.table_id is not None:
            result.table_id = row.table_id.decode('utf-8')
        if hasattr(row, 'table_url') and row.table_url is not None:
            result.table_url = row.table_url.decode('utf-8')
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
            'UPSERT INTO cabinets (id, client_id, created_at, title, invalid, token) '
            'VALUES ($cabinetId, $clientId, CurrentUTCTimestamp(), $title, False, $token)',
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
            'SELECT id, client_id, created_at, title, invalid, token, table_id, table_url FROM cabinets '
            'WHERE id=$cabinetId',
            cabinetId=id
        )
        return cls.parse_row(rows[0]) if rows else None

    @classmethod
    async def get_by_id_async(cls, id: str) -> Optional['CabinetSchema']:
        rows = await prepare_and_execute_query_async(
            'DECLARE $cabinetId AS String;'
            'SELECT id, client_id, created_at, title, invalid, token, table_id, table_url FROM cabinets '
            'WHERE id=$cabinetId',
            cabinetId=id
        )
        return cls.parse_row(rows[0]) if rows else None

    @classmethod
    def get_for_client(cls, client_id: str) -> List['CabinetSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, created_at, title, invalid, token, table_id, table_url FROM cabinets '
            'WHERE client_id=$clientId '
            'ORDER BY created_at ASC',
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
            'DELETE FROM cabinets WHERE id=$cabinetId;'
            'DELETE FROM barcode_feedbacks WHERE cabinet_id=$cabinetId;'
            'DELETE FROM brand_feedbacks WHERE cabinet_id=$cabinetId;',
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

    @classmethod
    def update_table_data(cls, id_: str, table_id: str, table_url: str):
        prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'DECLARE $tableId AS String;'
            'DECLARE $tableURL AS String;'
            'UPSERT INTO cabinets (id, table_id, table_url) VALUES ($cabinetId, $tableId, $tableURL)',
            cabinetId=id_,
            tableId=table_id,
            tableURL=table_url
        )

    @classmethod
    def check_can_create(cls, client_id: str) -> bool:
        count_rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT COUNT(id) AS cabs_count FROM cabinets WHERE client_id=$clientId',
            clientId=client_id
        )
        cap_row = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT cabinets_cap FROM clients WHERE id=$clientId',
            clientId=client_id
        )

        existing_cabinets = count_rows[0].cabs_count
        cabinets_cap = cap_row[0].cabinets_cap
        return existing_cabinets < cabinets_cap
