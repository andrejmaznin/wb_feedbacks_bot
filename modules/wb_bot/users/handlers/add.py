from typing import Dict, List, Optional, Union

from app.connections import bot
from modules.commands import Commands, finish_command
from modules.users import get_formatted_list_of_users, invite_user
from modules.wb_bot.markups.common import get_back_button_markup
from modules.wb_bot.markups.users import get_users_reply_markup


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
            command=Commands.USERS_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_users(client_id),
            reply_markup=get_users_reply_markup(),
            parse_mode='MarkdownV2'
        )
        return

    text = text.lstrip('@')

    if not text or not text.isascii() or text == str(message.from_user.id) or text == message.from_user.username:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас'
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите имя пользователя Telegram или Telegram ID пользователя',
            reply_markup=get_back_button_markup()
        )
        return

    invite_user(
        client_id=client_id,
        data=text
    )
    finish_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.USERS_ADD
    )

    bot.send_message(
        chat_id=message.from_user.id,
        text=f'Пользователь с данными `{text}` успешно добавлен',
        reply_markup=get_users_reply_markup(),
        parse_mode='MarkdownV2'
    )
    bot.send_message(
        chat_id=message.from_user.id,
        text=get_formatted_list_of_users(client_id),
        reply_markup=get_users_reply_markup(),
        parse_mode='MarkdownV2'
    )
