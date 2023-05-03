from typing import Optional, Union, List, Dict

from commands import finish_command, Commands
from connections import bot
from libs.ydb import prepare_and_execute_query
from logic.cabinets.internals import get_formatted_list_of_cabinets
from logic.cabinets.schemas import CabinetSchema
from markups.cabinets import get_cabinets_reply_markup
from markups.common import get_back_button_markup


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
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2'
        )
        return

    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DECLARE $title AS String;'
        'SELECT id FROM cabinets '
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
    CabinetSchema.delete_by_id(id=rows[0].id.decode('utf-8'))

    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.CABINETS_REMOVE
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text='Кабинет селлера успешно удален',
        reply_markup=get_cabinets_reply_markup(),
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text=get_formatted_list_of_cabinets(client_id),
        reply_markup=get_cabinets_reply_markup(),
        parse_mode='MarkdownV2'
    )
