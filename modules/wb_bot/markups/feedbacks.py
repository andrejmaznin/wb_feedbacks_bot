import telebot


def get_feedbacks_reply_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    add_button = telebot.types.KeyboardButton('✉️ Добавить ответ')
    exclude_button = telebot.types.KeyboardButton('⚠️ Исключить товар')
    import_button = telebot.types.KeyboardButton('📎 Импортировать ответы')
    default_button = telebot.types.KeyboardButton('📨 Ответы по умолчанию')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.row(add_button, exclude_button)
    markup.row(import_button, default_button)
    markup.row(back_button)
    return markup


def get_default_feedbacks_reply_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_button = telebot.types.KeyboardButton('✉️ Добавить ответ')
    remove_button = telebot.types.KeyboardButton('❌ Удалить ответ')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.row(add_button, remove_button)
    markup.row(back_button)
    return markup


def get_choice_default_reply_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    pos_button = telebot.types.KeyboardButton('➕ Положительные')
    neg_button = telebot.types.KeyboardButton('➖ Отрицательные')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.row(pos_button, neg_button)
    markup.row(back_button)
    return markup
