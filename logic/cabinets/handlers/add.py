from typing import Optional, Union, List, Dict

from commands import finish_command, Commands, update_command_metadata
from connections import bot
from logic.cabinets.internals import get_formatted_list_of_cabinets, check_cabinet_exists
from logic.cabinets.schemas import CabinetSchema
from markups.cabinets import get_cabinets_reply_markup
from markups.common import get_back_button_markup


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
            command=Commands.CABINETS_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2'
        )
        return

    if metadata['step'] == 'title':
        if check_cabinet_exists(client_id=client_id, title=text):
            bot.send_message(
                chat_id=message.from_user.id,
                text='Кабинет с таким названием уже существует! Введите название, которое еще не занято',
                reply_markup=get_back_button_markup()
            )
            return

        metadata['title'] = text
        metadata['step'] = 'wbtoken'
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите WBToken от вашего аккаунта продавца',
            reply_markup=get_back_button_markup()
        )

    elif metadata['step'] == 'wbtoken':
        metadata['wbtoken'] = text
        metadata['step'] = 'wildauthnew_v3'
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите ключ WILDAUTHNEW_V3 от вашего аккаунта продавца',
            reply_markup=get_back_button_markup()
        )

    elif metadata['step'] == 'wildauthnew_v3':
        metadata['wildauthnew_v3'] = text
        metadata['step'] = 'x_supplier_id'
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите Supplier ID вашего аккаунта продавца',
            reply_markup=get_back_button_markup()
        )

    elif metadata['step'] == 'x_supplier_id':
        metadata['x_supplier_id'] = text
        CabinetSchema.create(
            client_id=client_id,
            title=metadata['title'],
            wbtoken=metadata['wbtoken'],
            wildauthnew_v3=metadata['wildauthnew_v3'],
            x_supplier_id=metadata['x_supplier_id']
        )
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Кабинет селлера успешно добавлен!',
            reply_markup=get_cabinets_reply_markup()
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2'
        )
        return

    update_command_metadata(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.CABINETS_ADD,
        metadata=metadata
    )
