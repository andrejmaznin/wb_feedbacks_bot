from typing import Optional, Union, List, Dict

from telebot.types import ReplyKeyboardRemove

from commands import update_command_metadata, Commands, finish_command
from connections import bot
from libs.ydb import prepare_and_execute_query, get_or_generate_id
from markups.common import get_back_button_markup
from markups.root import get_root_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    if metadata is None or not isinstance(metadata, dict):
        return

    text = message.text

    if not text:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_back_button_markup()
        )
        return

    if metadata.get('step') == 0:
        metadata['wildauthnew_v3'] = text
        metadata['step'] += 1

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.UPDATE_AUTH_DATA,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите WBToken от вашего аккаунта продавца',
            reply_markup=ReplyKeyboardRemove()
        )

    elif metadata.get('step') == 1:
        metadata['wbtoken'] = text
        metadata['step'] += 1

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.UPDATE_AUTH_DATA,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите Supplier ID вашего аккаунта продавца',
            reply_markup=ReplyKeyboardRemove()
        )

    elif metadata.get('step') == 2:
        metadata['x_supplier_id'] = text
        metadata['step'] += 1

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.UPDATE_AUTH_DATA,
            metadata=metadata
        )
        cookie_id = get_or_generate_id(
            f'SELECT id FROM cookies WHERE client_id="{client_id}"'
        )

        prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'DECLARE $cookieId AS String;'
            'DECLARE $wbToken AS String;'
            'DECLARE $wildAuthNewV3 AS String;'
            'DECLARE $xSupplierId AS String;'
            'UPSERT INTO cookies (id, client_id, wbtoken, wildauthnew_v3, x_supplier_id) '
            'VALUES ($cookieId, $clientId, $wbToken, $wildAuthNewV3, $xSupplierId)',
            clientId=client_id,
            cookieId=cookie_id,
            wbToken=metadata['wbtoken'],
            wildAuthNewV3=metadata['wildauthnew_v3'],
            xSupplierId=metadata['x_supplier_id']
        )

        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.UPDATE_AUTH_DATA
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот готов к работе!',
            reply_markup=get_root_reply_markup(client_id)
        )
