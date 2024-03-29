from typing import Dict, List, Optional, Union

from app.connections import bot
from modules.cabinets.internals import (get_formatted_list_of_cabinets)
from modules.cabinets.schemas import CabinetSchema
from modules.commands import Commands, finish_command, initiate_command
from modules.wb_bot.markups.cabinets import get_cabinets_reply_markup
from modules.wb_bot.markups.common import get_back_button_markup
from modules.wb_bot.markups.root import get_root_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    command = message.text

    if command == '➕ Добавить кабинет':
        if not CabinetSchema.check_can_create(client_id=client_id):
            bot.send_message(
                chat_id=message.from_user.id,
                text='Вы достигли лимита кабинетов селлера в аккаунте!\n'
                     'Удалите существующий кабинет, чтобы добавить новый',
                reply_markup=get_cabinets_reply_markup(client_id=client_id)
            )
            bot.send_message(
                chat_id=message.from_user.id,
                text=get_formatted_list_of_cabinets(client_id=client_id),
                reply_markup=get_cabinets_reply_markup(client_id=client_id),
                parse_mode='MarkdownV2',
                disable_web_page_preview=True
            )
            return

        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_ADD,
            metadata={'step': 'title'}
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите название кабинета селлера',
            reply_markup=get_back_button_markup()
        )

    elif command == '❌ Удалить кабинет':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_REMOVE,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='`Внимание\!` Обязательно закройте вкладку с онлайн\-таблицей с ответами на отзывы перед удалением кабинета',
            reply_markup=get_back_button_markup(),
            parse_mode='MarkdownV2'
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите название кабинета из списка выше',
            reply_markup=get_back_button_markup()
        )

    elif command == '🔄 Обновить токен':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_UPDATE,
            metadata={'step': 'title'},
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите название кабинета из списка выше',
            reply_markup=get_back_button_markup()
        )


    elif command == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_root_reply_markup(client_id)
        )

    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_cabinets_reply_markup(client_id=client_id)
        )
