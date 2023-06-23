import telebot


def get_users_reply_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_button = telebot.types.KeyboardButton('👤️ Добавить аккаунт')
    delete_button = telebot.types.KeyboardButton('❌ Удалить аккаунт')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.add(add_button, delete_button, back_button)
    return markup
