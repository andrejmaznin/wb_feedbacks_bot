import telebot

from commands import initiate_command, Commands
from connections import bot
from logic.cabinets.exports import get_formatted_list_of_cabinets
from logic.onboarding.exports import initiate_onboarding
from logic.root.internals import start_bot, stop_bot
from logic.users.exports import get_formatted_list_of_users
from logic.users.utils import is_owner
from markups.cabinets import get_cabinets_reply_markup
from markups.feedbacks import get_feedbacks_reply_markup
from markups.root import get_root_reply_markup
from markups.users import get_users_reply_markup


def handler(message: telebot.types.Message, client_id: str):
    command = message.text

    if command == '🟢 Запустить бота':
        start_bot(client_id=client_id)
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот успешно запущен',
            reply_markup=get_root_reply_markup(client_id)
        )

    elif command == '🔴 Остановить бота':
        stop_bot(client_id=client_id)
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот успешно остановлен',
            reply_markup=get_root_reply_markup(client_id)
        )

    elif command == '📩 Ответы':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Выберите желаемое действие',
            reply_markup=get_feedbacks_reply_markup()
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
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2'
        )

    elif command == '⚙️ Настроить заново':
        initiate_onboarding(message, client_id)

    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_root_reply_markup(client_id)
        )
