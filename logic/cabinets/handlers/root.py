from typing import Optional, Union, List, Dict

from commands import initiate_command, Commands, finish_command
from connections import bot
from logic.cabinets.internals import get_formatted_list_of_cabinets, delete_invalid_cabinets_for_client
from markups.cabinets import get_cabinets_reply_markup
from markups.common import get_back_button_markup
from markups.root import get_root_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    command = message.text

    if command == '➕ Добавить кабинет':
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
            text='Введите название кабинета из списка выше',
            reply_markup=get_back_button_markup()
        )

    elif command == '🧹 Очистить неактивные':
        delete_invalid_cabinets_for_client(client_id=client_id)
        bot.send_message(
            chat_id=message.from_user.id,
            text='Неактивные кабинеты успешно удалены!',
            reply_markup=get_cabinets_reply_markup()
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id=client_id),
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2'
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
            reply_markup=get_cabinets_reply_markup()
        )
