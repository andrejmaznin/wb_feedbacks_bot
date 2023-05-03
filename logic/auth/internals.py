from telebot.types import ReplyKeyboardRemove

from commands import initiate_command, Commands
from connections import bot
from libs.ydb import prepare_and_execute_query


def check_cookie(client_id) -> bool:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'SELECT invalid_cookie FROM clients WHERE id=$clientId',
        clientId=client_id
    )

    if not rows or not rows[0].invalid_cookie:
        return True
    return False


def initiate_auth_data_update(client_id: str, telegram_id: int) -> None:
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'UPSERT INTO clients (id, invalid_cookie) VALUES ($clientId, False)',
        clientId=client_id
    )

    initiate_command(
        client_id=client_id,
        telegram_id=telegram_id,
        command=Commands.UPDATE_AUTH_DATA,
        metadata={'step': 0}
    )
    bot.send_message(
        chat_id=telegram_id,
        text='🤖 Судя по всему, указанные вами данные для аутентификации недействительны\n\n'
             'Ответьте на несколько вопросов, чтобы заполнить их заново',
        reply_markup=ReplyKeyboardRemove()
    )
    bot.send_message(
        chat_id=telegram_id,
        text='Введите ключ WILDAUTHNEW_V3 от вашего аккаунта продавца',
        reply_markup=ReplyKeyboardRemove()
    )
