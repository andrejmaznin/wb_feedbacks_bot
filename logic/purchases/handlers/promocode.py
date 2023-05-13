import uuid
from typing import Optional, Union, List, Dict

from commands import finish_command, Commands
from connections import bot
from libs.ydb import prepare_and_execute_query
from markups.common import get_back_button_markup
from markups.purchases import get_purchase_markup
from markups.root import get_root_reply_markup


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
            command=Commands.ENTER_PROMOCODE
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_purchase_markup()
        )
        return

    if not text or not text.isalpha():
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_back_button_markup()
        )
        return

    rows = prepare_and_execute_query(
        'DECLARE $code AS String;'
        'SELECT code FROM promocodes WHERE code=$code',
        code=text
    )

    if not rows:
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.ENTER_PROMOCODE
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Такого промокода не существует',
            reply_markup=get_purchase_markup()
        )
        return

    purchase_id = str(uuid.uuid4())
    prepare_and_execute_query(
        'DECLARE $purchaseId AS String;'
        'DECLARE $clientId AS String;'
        'DECLARE $userId AS String;'
        'DECLARE $code AS String;'
        'UPSERT INTO purchases (id, client_id, date, execute) '
        f'VALUES ($purchaseId, $clientId, CurrentUtcDate(), False);'
        f'UPSERT INTO users (id, owner) VALUES ($userId, True);'
        f'DELETE FROM promocodes WHERE code=$code',
        purchaseId=purchase_id,
        clientId=client_id,
        userId=metadata['user_id'],
        code=text
    )
    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.ENTER_PROMOCODE
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text='✅ Поздравляем, промокод действителен\!',
        parse_mode='MarkdownV2',
    )

    bot.send_message(
        chat_id=message.from_user.id,
        text='Бот готов к работе\!\nДобавьте ваш первый кабинет селлера в соответствующем разделе',
        parse_mode='MarkdownV2',
        reply_markup=get_root_reply_markup(client_id)
    )
