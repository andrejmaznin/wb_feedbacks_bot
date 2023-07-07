import logging
from typing import Dict, List, Optional, Union

from app.connections import bot
from libs.ydb import prepare_and_execute_query
from modules.cabinets.internals import get_formatted_list_of_cabinets
from modules.commands import Commands, finish_command, update_command_metadata
from modules.wb_bot.markups.cabinets import get_cabinets_reply_markup
from modules.wb_bot.markups.common import get_back_button_markup

logger = logging.getLogger(__name__)


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
            command=Commands.CABINETS_UPDATE
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
        return

    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DECLARE $title AS String;'
        'SELECT id, table_id FROM cabinets '
        'WHERE client_id=$clientId AND title=$title;',
        clientId=client_id,
        title=text
    )

    if metadata['step'] == 'title':
        if not rows:
            bot.send_message(
                chat_id=message.from_user.id,
                text='Кабинета с таким названием нет в вашем аккаунте',
                reply_markup=get_back_button_markup(),
            )
            return

        metadata['step'] = 'token'
        metadata['id'] = rows[0].id.decode('utf-8')
        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_UPDATE,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите новый Стандартный API токен от вашего аккаунта продавца',
            reply_markup=get_back_button_markup()
        )
    elif metadata['step'] == 'token':
        if not text.isascii():
            bot.send_message(
                chat_id=message.from_user.id,
                text='Не поняли вас',
                reply_markup=get_back_button_markup()
            )
            return

        prepare_and_execute_query(
            'DECLARE $cabinetId AS String;'
            'DECLARE $token AS String;'
            'UPSERT INTO cabinets (id, token) VALUES ($cabinetId, $token)',
            cabinetId=metadata['id'],
            token=text
        )

        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_UPDATE
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Токен кабинета селлера успешно обновлён!',
            reply_markup=get_cabinets_reply_markup()
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
