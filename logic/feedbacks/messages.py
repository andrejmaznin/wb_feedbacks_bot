import logging
from typing import List, Tuple

from telebot.formatting import escape_markdown

from logic.feedbacks.schemas import FeedbackSchema

logger = logging.getLogger(__name__)


def escape_punctuation(string: str) -> str:
    string = string.replace('!', '\!')
    string = string.replace('.', '\.')
    string = string.replace('-', '\-')
    return string


def format_list_of_default_feedbacks(
    pos_feedbacks: List[FeedbackSchema],
    neg_feedbacks: List[FeedbackSchema]
) -> Tuple[str, dict]:
    title = 'Вот список ваших ответов на отзывы по умолчанию'
    pos_title = '➕ Ответы на положительные (4-5 звёзд) отзывы:'
    neg_title = '➖ Ответы на отрицательные (1-3 звезды) отзывы:'
    pos_text = ''
    neg_text = ''

    metadata = {}
    for counter, feedback in enumerate(pos_feedbacks + neg_feedbacks, start=1):
        metadata[counter] = feedback.id

        if feedback.neg_feedback is None and feedback.pos_feedback is not None:
            pos_text += escape_markdown(f'`{counter}`\. _{escape_punctuation(feedback.pos_feedback)}_\n')
        elif feedback.pos_feedback is None and feedback.neg_feedback is not None:
            neg_text += escape_markdown(f'`{counter}`\. _{escape_punctuation(feedback.neg_feedback)}_\n')

    formatted_text = escape_markdown(f'{title}\n\n{pos_title}\n{pos_text}\n{neg_title}\n{neg_text}')
    return formatted_text, metadata
