from typing import Optional, Union, List, Dict

from commands import finish_command, Commands, initiate_command
from connections import bot
from markups.common import get_back_button_markup
from markups.feedbacks import get_feedbacks_reply_markup


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
            command=Commands.FEEDBACKS_ADD_BARCODE
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_feedbacks_reply_markup()
        )
        return

    if not text or not text.isdigit():
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_back_button_markup()
        )
        return

    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.FEEDBACKS_ADD_BARCODE
    )
    initiate_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.FEEDBACKS_ADD_TEXT,
        metadata={'barcode': text}
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text='Введите текст ответа на отзыв о данном товаре',
        reply_markup=get_back_button_markup()
    )
