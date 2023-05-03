import telebot


def get_purchase_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    buy_button = telebot.types.KeyboardButton('💰 Оформить подписку')
    promocode_button = telebot.types.KeyboardButton('🎁 Ввести промокод')
    markup.add(buy_button, promocode_button)
    return markup
