import telebot


def get_yes_no_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    yes_button = telebot.types.KeyboardButton('Да')
    no_button = telebot.types.KeyboardButton('Нет')
    markup.add(yes_button, no_button)
    return markup


def get_yes_no_back_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    yes_button = telebot.types.KeyboardButton('Да')
    no_button = telebot.types.KeyboardButton('Нет')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.add(yes_button, no_button, back_button)
    return markup
