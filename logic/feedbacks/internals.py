from typing import Tuple

from libs.ydb import prepare_and_execute_query
from logic.feedbacks.messages import format_list_of_default_feedbacks
from logic.feedbacks.schemas import FeedbackSchema


def get_formatted_list_of_feedbacks(client_id: str) -> Tuple[str, dict]:
    pos_feedbacks = FeedbackSchema.get_positive_for_client(client_id=client_id)
    neg_feedbacks = FeedbackSchema.get_negative_for_client(client_id=client_id)
    return format_list_of_default_feedbacks(
        pos_feedbacks=pos_feedbacks,
        neg_feedbacks=neg_feedbacks
    )


def set_complaints(client_id: str, complain: bool):
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DECLARE $complain AS Bool;'
        '$settingsId = SELECT id FROM settings WHERE client_id = $clientId;'
        'UPSERT INTO settings (id, complain) VALUES ($settingsId, $complain)',
        clientId=client_id,
        complain=complain
    )
