from typing import List, Mapping, Optional

from pydantic import BaseModel, Field

from libs.wildberries.schemas import ReviewSchema
from libs.ydb.utils import prepare_and_execute_query_async, prepare_and_execute_query


class BarcodeFeedbackSchema(BaseModel):
    barcode: bytes
    cabinet_id: bytes
    pos_feedback: bytes


class BrandFeedbackSchema(BaseModel):
    brand: bytes
    cabinet_id: bytes
    pos_feedbacks: bytes


class ScanCabinetTask(BaseModel):
    cabinet_id: str = Field(..., alias='cabinetId')
    client_id: str = Field(..., alias='clientId')


class ReplyCabinetTask(BaseModel):
    cabinet_id: str = Field(..., alias='cabinetId')
    client_id: str = Field(..., alias='clientId')
    reviews: List[ReviewSchema]


class UpdateFeedbacksTask(BaseModel):
    cabinet_id: str = Field(..., alias='cabinetId')
    table_id: str = Field(..., alias='tableId')


class ReplySettingsSchema(BaseModel):
    id: str
    client_id: str
    complain: bool

    @classmethod
    def parse_row(cls, row: Mapping) -> Optional['ReplySettingsSchema']:
        if not all([hasattr(row, 'id'), hasattr(row, 'client_id'), hasattr(row, 'complain')]):
            return None

        result = cls(
            id=row.id.decode('utf-8'),
            client_id=row.client_id.decode('utf-8'),
            complain=row.complain
        )
        return result

    @classmethod
    async def get_for_client_async(cls, client_id: str) -> Optional['ReplySettingsSchema']:
        rows = await prepare_and_execute_query_async(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, complain FROM settings WHERE client_id=$clientId '
            'LIMIT 1',
            clientId=client_id
        )
        return cls.parse_row(rows[0]) if rows else None

    @classmethod
    def get_for_client(cls, client_id: str) -> Optional['ReplySettingsSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, complain FROM settings WHERE client_id=$clientId '
            'LIMIT 1',
            clientId=client_id
        )
        return cls.parse_row(rows[0]) if rows else None

    def set_complaints(self, complain: bool) -> None:
        prepare_and_execute_query(
            'DECLARE $settingsId AS String;'
            'DECLARE $complain AS Bool;'
            'UPSERT INTO settings (id, complain) VALUES ($settingsId, $complain)',
            settingsId=self.id,
            complain=complain
        )
