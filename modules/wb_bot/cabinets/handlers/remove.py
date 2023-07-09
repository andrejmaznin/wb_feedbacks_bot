from typing import Dict, List, Optional, Union

from app.connections import bot
from libs.microsoft import get_ms_client
from libs.ydb import prepare_and_execute_query
from modules.cabinets.internals import get_formatted_list_of_cabinets
from modules.cabinets.schemas import CabinetSchema
from modules.commands import Commands, finish_command
from modules.wb_bot.markups.cabinets import get_cabinets_reply_markup
from modules.wb_bot.markups.common import get_back_button_markup


def handler(
        message,
        client_id: str,
        metadata: Optional[Union[List, Dict]] = None
):
    text = message.text

    if not text:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_back_button_markup(),
        )
        return

    if text == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_REMOVE
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(client_id=client_id),
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
    if not rows:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Кабинета с таким названием нет в вашем аккаунте',
            reply_markup=get_back_button_markup(),
        )
        return

    ms_client = get_ms_client()
    CabinetSchema.delete_by_id(id=rows[0].id.decode('utf-8'))
    ms_client.delete_item(item_id=rows[0].table_id.decode('utf-8'))

    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.CABINETS_REMOVE
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text='Кабинет селлера успешно удален',
        reply_markup=get_cabinets_reply_markup(client_id=client_id),
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text=get_formatted_list_of_cabinets(client_id),
        reply_markup=get_cabinets_reply_markup(client_id=client_id),
        parse_mode='MarkdownV2',
        disable_web_page_preview=True
    )
