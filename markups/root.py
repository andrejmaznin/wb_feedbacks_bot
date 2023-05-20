import telebot

from libs.ydb import prepare_and_execute_query


def get_root_reply_markup(client_id):
    execute = prepare_and_execute_query(
        f'DECLARE $clientId AS String;'
        f'SELECT execute FROM purchases WHERE client_id=$clientId',
        clientId=client_id
    )[0].execute
    complain = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'SELECT complain FROM settings WHERE client_id=$clientId',
        clientId=client_id
    )[0].complain

    if execute:
        start_button = telebot.types.KeyboardButton('🔴 Остановить бота')
    else:
        start_button = telebot.types.KeyboardButton('🟢 Запустить бота')
    if complain:
        complain_button = telebot.types.KeyboardButton('🔇 Не жаловаться')
    else:
        complain_button = telebot.types.KeyboardButton('🔈 Жаловаться')

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    feedbacks_button = telebot.types.KeyboardButton('📩 Ответы')
    people_button = telebot.types.KeyboardButton('👥 Пользователи')
    cabinets_button = telebot.types.KeyboardButton('💼 Кабинеты селлера')
    markup.row(start_button, complain_button)
    markup.row(feedbacks_button)
    markup.row(cabinets_button, people_button)
    return markup
