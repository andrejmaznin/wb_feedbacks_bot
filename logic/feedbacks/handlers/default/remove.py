from typing import Dict, List, Union, Optional

from commands import finish_command, Commands
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
            command=Commands.FEEDBACKS_DEFAULT_REMOVE
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_feedbacks(client_id=client_id)[0],
            reply_markup=get_default_feedbacks_reply_markup(),
            parse_mode='MarkdownV2'
        )
        return

    if not text.isdigit() or text not in metadata.keys():
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_back_button_markup()
        )
        return
    FeedbackSchema.delete_by_id(id=metadata.get(text))

    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.FEEDBACKS_DEFAULT_REMOVE
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text='Ответ по умолчанию успешно удален',
        reply_markup=get_default_feedbacks_reply_markup()
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text=get_formatted_list_of_feedbacks(client_id=client_id)[0],
        reply_markup=get_default_feedbacks_reply_markup(),
        parse_mode='MarkdownV2'
    )
