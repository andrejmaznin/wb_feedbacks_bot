from typing import Optional, Union, List, Dict

from commands import initiate_command, Commands, finish_command
from connections import bot
from markups.common import get_back_button_markup
from markups.feedbacks import get_feedbacks_reply_markup, get_default_feedbacks_reply_markup, \
    get_choice_default_reply_markup


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    command = message.text

    if command == '✉️ Добавить ответ':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_DEFAULT_ADD,
            metadata={'step': 'choice'}
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Это ответ на положительные или отрицательные отзывы?',
            reply_markup=get_choice_default_reply_markup()
        )

    elif command == '❌ Удалить ответ':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_DEFAULT_REMOVE,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите номер ответа из списка выше',
            reply_markup=get_back_button_markup()
        )

    elif command == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_DEFAULT
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_feedbacks_reply_markup()
        )

    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_default_feedbacks_reply_markup()
        )
