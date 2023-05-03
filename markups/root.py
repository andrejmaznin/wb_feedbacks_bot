import telebot

from connections import get_session_pool


def get_root_reply_markup(client_id):
    pool = get_session_pool()

    with pool.checkout() as session:
        execute = session.transaction().execute(
            f'SELECT execute FROM purchases WHERE client_id = "{client_id}"',
            commit_tx=True
        )[0].rows[0].execute

    if execute:
        start_button = telebot.types.KeyboardButton('🔴 Остановить бота')
    else:
        start_button = telebot.types.KeyboardButton('🟢 Запустить бота')

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    feedbacks_button = telebot.types.KeyboardButton('📩 Ответы')
    people_button = telebot.types.KeyboardButton('👥 Пользователи')
    settings_button = telebot.types.KeyboardButton('💼 Кабинеты селлера')
    markup.add(start_button, feedbacks_button, people_button, settings_button)
    return markup
