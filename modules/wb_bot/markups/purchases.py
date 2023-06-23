import telebot


def get_purchase_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    subscription_button = telebot.types.KeyboardButton('✅ Оформить подписку')
    promocode_button = telebot.types.KeyboardButton('🎁 Ввести промокод')
    markup.add(subscription_button, promocode_button)
    return markup


def get_subscription_plans_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    plan_1 = telebot.types.KeyboardButton('1️⃣ До 1 кабинета')
    plan_2 = telebot.types.KeyboardButton('2️⃣ До 3 кабинетов')
    plan_3 = telebot.types.KeyboardButton('3️⃣ До 5 кабинетов')
    back_button = telebot.types.KeyboardButton('◀️ Назад')
    markup.row(plan_1)
    markup.row(plan_2)
    markup.row(plan_3)
    markup.row(back_button)
    return markup


def get_promocode_reply_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    promocode_button = telebot.types.KeyboardButton('🎁 Ввести промокод')
    markup.add(promocode_button)
    return markup
