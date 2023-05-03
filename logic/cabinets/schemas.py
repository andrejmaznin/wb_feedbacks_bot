from typing import List, Mapping, Optional

from pydantic import BaseModel

from libs.ydb import get_or_generate_id, prepare_and_execute_query


class CabinetSchema(BaseModel):
    id: str
    client_id: str
    title: str
    invalid: bool
    wbtoken: Optional[str] = None
    wildauthnew_v3: Optional[str] = None
    x_supplier_id: Optional[str] = None

    @classmethod
    def parse_rows(cls, rows: List[Mapping]) -> List['CabinetSchema']:
        results = []
        for row in rows:
            if user := cls.parse_row(row):
                results.append(user)
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
        if hasattr(row, 'title') and row.title is not None:
            result.title = row.title.decode('utf-8')
        if hasattr(row, 'wbtoken') and row.wbtoken is not None:
            result.wbtoken = row.wbtoken.decode('utf-8')
        if hasattr(row, 'wildauthnew_v3') and row.wildauthnew_v3 is not None:
            result.wildauthnew_v3 = row.wildauthnew_v3.decode('utf-8')
        if hasattr(row, 'x_supplier_id') and row.x_supplier_id is not None:
            result.x_supplier_id = row.x_supplier_id.decode('utf-8')
        return result

    @classmethod
    def create(
        cls,
        client_id: str,
        title: str,
        wbtoken: str,
        wildauthnew_v3: str,
        x_supplier_id: str
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
            'DECLARE $wbToken AS String;'
            'DECLARE $wildAuthNewV3 AS String;'
            'DECLARE $xSupplierId AS String;'
            'UPSERT INTO cabinets (id, client_id, title, invalid, wbtoken, wildauthnew_v3, x_supplier_id) '
            'VALUES ($cabinetId, $clientId, $title, False, $wbToken, $wildAuthNewV3, $xSupplierId)',
            cabinetId=cabinet_id,
            clientId=client_id,
            title=title,
            wbToken=wbtoken,
            wildAuthNewV3=wildauthnew_v3,
            xSupplierId=x_supplier_id
        )
        return cls.get_by_id(cabinet_id)

    @classmethod
    def get_by_id(cls, id: str) -> Optional['CabinetSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'SELECT id, client_id, title, invalid, wbtoken, wildauthnew_v3, x_supplier_id FROM cabinets '
            'WHERE id=$cabinetId;',
            cabinetId=id
        )
        return cls.parse_row(rows[0]) if rows else None

    @classmethod
    def get_for_client(cls, client_id: str) -> List['CabinetSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, title, invalid, wbtoken, wildauthnew_v3, x_supplier_id FROM cabinets '
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
    def delete_by_id(cls, id: str):
        prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'DELETE FROM cabinets WHERE id=$cabinetId',
            cabinetId=id
        )
