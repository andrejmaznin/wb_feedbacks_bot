import telebot


def get_back_button_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.add(back_button)
    return markup
