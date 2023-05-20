import telebot


def get_purchase_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    subscription_button = telebot.types.KeyboardButton('✅ Оформить подписку')
    promocode_button = telebot.types.KeyboardButton('🎁 Ввести промокод')
    markup.add(subscription_button, promocode_button)
    return markup


def get_confirm_subscription_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    buy_button = telebot.types.KeyboardButton('💰 Оплата')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.add(buy_button, back_button)
    return markup
