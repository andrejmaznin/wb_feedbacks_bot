from typing import Tuple

from logic.feedbacks.messages import format_list_of_default_feedbacks
from logic.feedbacks.schemas import FeedbackSchema


def get_formatted_list_of_feedbacks(client_id: str) -> Tuple[str, dict]:
    pos_feedbacks = FeedbackSchema.get_positive_for_client(client_id=client_id)
    neg_feedbacks = FeedbackSchema.get_negative_for_client(client_id=client_id)
    return format_list_of_default_feedbacks(
        pos_feedbacks=pos_feedbacks,
        neg_feedbacks=neg_feedbacks
    )
