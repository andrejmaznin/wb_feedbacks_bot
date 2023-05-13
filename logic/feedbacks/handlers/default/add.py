from typing import Dict, List, Union, Optional

from commands import finish_command, Commands, update_command_metadata
from connections import bot
from logic.feedbacks.internals import get_formatted_list_of_feedbacks
from logic.feedbacks.schemas import FeedbackSchema
from markups.common import get_back_button_markup
from markups.feedbacks import get_default_feedbacks_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    text = message.text

    if text == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_DEFAULT_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_feedbacks(client_id=client_id)[0],
            reply_markup=get_default_feedbacks_reply_markup(),
            parse_mode='MarkdownV2'
        )
        return

    if metadata['step'] == 'choice':
        if text == '➕ Положительные':
            metadata['kind'] = 'positive'
        elif text == '➖ Отрицательные':
            metadata['kind'] = 'negative'

        metadata['step'] = 'text'
        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_DEFAULT_ADD,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите текст ответа на отзывы по умолчанию',
            reply_markup=get_back_button_markup()
        )

    elif metadata['step'] == 'text':
        if metadata['kind'] == 'positive':
            FeedbackSchema.create_positive(
                client_id=client_id,
                pos_feedback=text
            )
        elif metadata['kind'] == 'negative':
            FeedbackSchema.create_negative(
                client_id=client_id,
                neg_feedback=text
            )

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_DEFAULT,
            metadata=get_formatted_list_of_feedbacks(client_id=client_id)[1]
        )
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_DEFAULT_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Ответ по умолчанию успешно добавлен!',
            reply_markup=get_default_feedbacks_reply_markup()
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_feedbacks(client_id)[0],
            reply_markup=get_default_feedbacks_reply_markup(),
            parse_mode='MarkdownV2'
        )

    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_default_feedbacks_reply_markup()
        )
