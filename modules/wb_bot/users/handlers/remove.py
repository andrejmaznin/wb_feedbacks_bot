from typing import Dict, List, Optional, Union

from connections import bot
from modules.commands import Commands, finish_command
from modules.users.internals import delete_user, get_formatted_list_of_users
from modules.wb_bot.markups.common import get_back_button_markup
from modules.wb_bot.markups.users import get_users_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    text = message.text
    if text == '◀️ Назад':
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_users(client_id),
            reply_markup=get_users_reply_markup(),
            parse_mode='MarkdownV2'
        )
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USERS_REMOVE
        )
        return

    success = delete_user(
        client_id=client_id,
        data=text.lstrip('@'),
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    if not success:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас'
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите данные пользователя из списка выше',
            reply_markup=get_back_button_markup()
        )
        return

    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.USERS_REMOVE
    )

    bot.send_message(
        chat_id=message.from_user.id,
        text=f'Пользователь с данными `{text}` успешно удален',
        reply_markup=get_users_reply_markup(),
        parse_mode='MarkdownV2'
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text=get_formatted_list_of_users(client_id),
        reply_markup=get_users_reply_markup(),
        parse_mode='MarkdownV2'
    )
