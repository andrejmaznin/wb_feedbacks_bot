import telebot


def get_feedbacks_reply_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_button = telebot.types.KeyboardButton('✉️ Добавить ответ')
    exclude_button = telebot.types.KeyboardButton('⚠️ Исключить товар')
    import_button = telebot.types.KeyboardButton('📎 Импортировать ответы')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.row(add_button, exclude_button)
    markup.row(import_button)
    markup.row(back_button)
    return markup
