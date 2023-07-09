import telebot

from modules.cabinets import CabinetSchema


def get_cabinets_reply_markup(client_id: str):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_button = telebot.types.KeyboardButton('➕ Добавить кабинет')
    remove_button = telebot.types.KeyboardButton('❌ Удалить кабинет')
    update_button = telebot.types.KeyboardButton('🔄 Обновить токен')
    back_button = telebot.types.KeyboardButton('◀️ Назад')

    markup.row(add_button, remove_button)

    cabs_count = CabinetSchema.count_for_client(client_id=client_id)
    if cabs_count != 0:
        markup.row(update_button)

    markup.row(back_button)
    return markup
