import json

import telebot

from app.connections import bot, get_update_queue
from modules.cabinets.exports import get_formatted_list_of_cabinets
from modules.cabinets.internals import get_refresh_messages_for_client
from modules.commands import Commands, initiate_command
from modules.feedbacks.schemas import ReplySettingsSchema
from modules.users.exports import get_formatted_list_of_users
from modules.users.utils import is_owner
from modules.wb_bot.markups.cabinets import get_cabinets_reply_markup
from modules.wb_bot.markups.root import get_root_reply_markup
from modules.wb_bot.markups.users import get_users_reply_markup
from modules.wb_bot.root.internals import start_bot, stop_bot


def handler(message: telebot.types.Message, client_id: str):
    command = message.text

    if command == '🟢 Запустить бота':
        start_bot(client_id=client_id)
        print('Started bot')
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот успешно запущен',
            reply_markup=get_root_reply_markup(client_id=client_id)
        )

    elif command == '🔴 Остановить бота':
        stop_bot(client_id=client_id)
        print('Stopped bot')
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот успешно остановлен',
            reply_markup=get_root_reply_markup(client_id=client_id)
        )

    elif command == '🔈 Жаловаться':
        settings = ReplySettingsSchema.get_for_client(client_id=client_id)
        settings.set_complaints(complain=True)
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот будет жаловаться на негативные (1-3 звезды) отзывы',
            reply_markup=get_root_reply_markup(client_id=client_id)
        )

    elif command == '🔇 Не жаловаться':
        settings = ReplySettingsSchema.get_for_client(client_id=client_id)
        settings.set_complaints(complain=False)
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот не будет жаловаться на негативные (1-3 звезды) отзывы',
            reply_markup=get_root_reply_markup(client_id=client_id)
        )

    elif command == '🔄 Обновить ответы':
        update_queue = get_update_queue()

        tasks = get_refresh_messages_for_client(client_id=client_id)
        for task in tasks:
            update_queue.send_message(
                MessageBody=json.dumps(task)
            )

        bot.send_message(
            chat_id=message.from_user.id,
            text='Ответы на отзывы обновляются!',
            reply_markup=get_root_reply_markup(client_id=client_id)
        )

    elif command == '👥 Пользователи':
        markup = None
        if is_owner(
            client_id=client_id,
            telegram_id=message.from_user.id,
            username=message.from_user.username
        ):
            initiate_command(
                client_id=client_id,
                telegram_id=message.from_user.id,
                command=Commands.USERS
            )
            markup = get_users_reply_markup()

        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_users(client_id),
            reply_markup=markup,
            parse_mode='MarkdownV2'
        )

    elif command == '💼 Кабинеты селлера':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(client_id=client_id),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )

    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_root_reply_markup(client_id)
        )
