from typing import Optional, Union, List, Dict

from commands import Commands, finish_command
from connections import bot
from libs.ydb import prepare_and_execute_query
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
            command=Commands.FEEDBACKS_EXCLUDE
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

    prepare_and_execute_query(
        'DECLARE $barcode AS String;'
        'DECLARE $clientId AS String;'
        'DELETE FROM barcode_feedbacks WHERE barcode=$barcode AND client_id=$clientId;'
        'UPSERT INTO exclude_feedbacks (barcode, client_id) VALUES ($barcode, $clientId);',
        barcode=message.text,
        clientId=client_id
    )

    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.FEEDBACKS_EXCLUDE
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text='Мы не будем отвечать на отзывы об этом товаре',
        reply_markup=get_feedbacks_reply_markup()
    )
