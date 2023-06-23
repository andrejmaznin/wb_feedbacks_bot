import telebot


def get_cabinets_reply_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_button = telebot.types.KeyboardButton('➕ Добавить кабинет')
    remove_button = telebot.types.KeyboardButton('❌ Удалить кабинет')
    clear_button = telebot.types.KeyboardButton('🧹 Очистить неактивные')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.row(add_button, remove_button)
    markup.row(clear_button)
    markup.row(back_button)
    return markup
