from typing import Dict, List, Optional, Union

from connections import bot
from modules.commands import Commands, finish_command, initiate_command
from modules.wb_bot.markups.common import get_back_button_markup
from modules.wb_bot.markups.root import get_root_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    command = message.text

    if command == '👤️ Добавить аккаунт':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USERS_ADD,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите имя пользователя Telegram или Telegram ID пользователя',
            reply_markup=get_back_button_markup()
        )

    elif command == '❌ Удалить аккаунт':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USERS_REMOVE,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите данные пользователя из списка выше',
            reply_markup=get_back_button_markup()
        )

    elif command == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USERS
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
            reply_markup=get_back_button_markup()
        )
