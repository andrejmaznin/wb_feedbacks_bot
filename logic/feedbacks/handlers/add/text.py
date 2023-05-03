from typing import Dict

from commands import finish_command, Commands
from connections import bot
from libs.ydb import prepare_and_execute_query
from markups.feedbacks import get_feedbacks_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Dict
):
    text = message.text
    if text == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_ADD_TEXT
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_feedbacks_reply_markup()
        )
        return

    prepare_and_execute_query(
        'DECLARE $barcode AS String;'
        'DECLARE $clientId AS String;'
        'DECLARE $posFeedback AS String;'
        'UPSERT INTO barcode_feedbacks (barcode, client_id, pos_feedback) '
        'VALUES ($barcode, $clientId, $posFeedback)',
        barcode=metadata.get('barcode'),
        clientId=client_id,
        posFeedback=text
    )

    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.FEEDBACKS_ADD_TEXT
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text='Ответ на отзыв успешно добавлен!',
        reply_markup=get_feedbacks_reply_markup()
    )
