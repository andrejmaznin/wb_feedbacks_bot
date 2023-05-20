import json
import logging
import uuid
from datetime import datetime
from typing import Mapping, Optional, List

from pydantic import BaseModel

from libs.ydb import prepare_and_execute_query
from libs.ydb.utils import prepare_and_execute_query_async

logger = logging.getLogger(__name__)


class ReviewSchema(BaseModel):
    id: str
    stars: int
    text: Optional[str] = None
    barcode: str
    brand: str


class SettingsSchema(BaseModel):
    id: str
    client_id: str
    complain: bool
    reply_neg: bool

    @classmethod
    def parse_row(cls, row: Mapping) -> Optional['SettingsSchema']:
        if not all([
            hasattr(row, 'id'), hasattr(row, 'client_id'), hasattr(row, 'complain'), hasattr(row, 'reply_neg')
        ]):
            return None
        if not all([row.id, row.client_id]):
            return None

        result = cls(
            id=row.id.decode('utf-8'),
            client_id=row.client_id.decode('utf-8'),
            complain=row.complain,
            reply_neg=row.reply_neg
        )
        return result

    @classmethod
    def get_for_client(cls, client_id: str) -> Optional['SettingsSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, complain, reply_neg FROM settings '
            'WHERE client_id=$clientId',
            clientId=client_id
        )
        return cls.parse_row(rows[0]) if rows else None

    @classmethod
    async def get_for_client_async(cls, client_id: str) -> Optional['SettingsSchema']:
        rows = await prepare_and_execute_query_async(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, complain, reply_neg FROM settings '
            'WHERE client_id=$clientId',
            clientId=client_id
        )
        return cls.parse_row(rows[0]) if rows else None


class FeedbackSchema(BaseModel):
    id: str
    client_id: str
    brands: List[str] = []
    created_at: datetime
    pos_feedback: Optional[str] = None
    neg_feedback: Optional[str] = None

    @classmethod
    def parse_row(cls, row: Mapping) -> Optional['FeedbackSchema']:
        if not all([
            hasattr(row, 'id'), hasattr(row, 'client_id'), hasattr(row, 'created_at')
        ]):
            return None
        if not all([row.id, row.client_id, row.created_at]):
            return None
        result = cls(
            id=row.id.decode('utf-8'),
            client_id=row.client_id.decode('utf-8'),
            created_at=row.created_at
        )

        if row.get('brands') is not None:
            result.brands = json.loads(row.brands)
        if row.get('pos_feedback') is not None:
            result.pos_feedback = row.pos_feedback.decode('utf-8')
        if row.get('neg_feedback') is not None:
            result.neg_feedback = row.neg_feedback.decode('utf-8')
        return result

    @classmethod
    def parse_rows(cls, rows: List[Mapping]) -> List['FeedbackSchema']:
        results = []
        for row in rows:
            if feedback := cls.parse_row(row):
                results.append(feedback)
        return results

    @classmethod
    def get_by_id(cls, id: str) -> Optional['FeedbackSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $feedbackId AS String;'
            'SELECT id, client_id, brands, created_at, pos_feedback, neg_feedback FROM feedbacks '
            'WHERE id=$feedbackId',
            feedbackId=id
        )
        return cls.parse_row(rows[0]) if rows else None

    @classmethod
    def create_positive(cls, client_id: str, pos_feedback: str) -> 'FeedbackSchema':
        feedback_id = str(uuid.uuid4())
        prepare_and_execute_query(
            'DECLARE $feedbackId AS String;'
            'DECLARE $clientId AS String;'
            'DECLARE $posFeedback AS String;'
            'UPSERT INTO feedbacks (id, client_id, pos_feedback, created_at) '
            'VALUES ($feedbackId, $clientId, $posFeedback, CurrentUtcTimestamp())',
            feedbackId=feedback_id,
            clientId=client_id,
            posFeedback=pos_feedback
        )
        return cls.get_by_id(feedback_id)

    @classmethod
    def create_negative(cls, client_id: str, neg_feedback: str) -> 'FeedbackSchema':
        feedback_id = str(uuid.uuid4())
        prepare_and_execute_query(
            'DECLARE $feedbackId AS String;'
            'DECLARE $clientId AS String;'
            'DECLARE $negFeedback AS String;'
            'UPSERT INTO feedbacks (id, client_id, neg_feedback, created_at) '
            'VALUES ($feedbackId, $clientId, $negFeedback, CurrentUtcTimestamp())',
            feedbackId=feedback_id,
            clientId=client_id,
            negFeedback=neg_feedback
        )
        return cls.get_by_id(feedback_id)

    @classmethod
    def get_positive_for_client(cls, client_id: str) -> List['FeedbackSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, created_at, pos_feedback FROM feedbacks '
            'WHERE client_id=$clientId AND neg_feedback IS NULL AND barcode IS NULL AND brands IS NULL',
            clientId=client_id
        )
        return cls.parse_rows(rows)

    @classmethod
    def get_negative_for_client(cls, client_id: str) -> List['FeedbackSchema']:
        rows = prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'SELECT id, client_id, created_at, neg_feedback FROM feedbacks '
            'WHERE client_id=$clientId AND pos_feedback IS NULL AND barcode IS NULL AND brands IS NULL',
            clientId=client_id
        )
        return cls.parse_rows(rows)

    @classmethod
    def delete_by_id(cls, id: str) -> None:
        prepare_and_execute_query(
            'DECLARE $feedbackId AS String;'
            'DELETE FROM feedbacks WHERE id=$feedbackId',
            feedbackId=id
        )
