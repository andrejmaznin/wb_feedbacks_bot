from typing import Optional, Union, List, Dict

from commands import initiate_command, Commands, finish_command
from connections import bot
from markups.common import get_back_button_markup
from markups.feedbacks import get_feedbacks_reply_markup
from markups.root import get_root_reply_markup


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
            command=Commands.FEEDBACKS_ADD_BARCODE,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите артикул товара на WB',
            reply_markup=get_back_button_markup()
        )

    elif command == '⚠️ Исключить товар':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_EXCLUDE,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите артикул товара на WB, на отзывы о котором бот не должен отвечать',
            reply_markup=get_back_button_markup()
        )

    elif command == '📎 Импортировать ответы':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_FILE_IMPORT,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Пожалуйста, заполните таблицу-образец и отправьте ее',
            reply_markup=get_back_button_markup()
        )
        # TODO: move to google cloud
        with open('Пример таблицы.xlsx', 'rb') as file:
            bot.send_document(
                chat_id=message.from_user.id,
                document=file
            )

    elif command == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS
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
            reply_markup=get_feedbacks_reply_markup()
        )
