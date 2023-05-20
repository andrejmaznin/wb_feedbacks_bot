import os

from commands import initiate_command, Commands
from connections import bot
from logic.purchases.consts import OFFER_MESSAGE_TEXT
from logic.purchases.messages import send_paywall_message
from markups.common import get_back_button_markup
from markups.purchases import get_confirm_subscription_markup


def handler(message, client_id: str, user_id: str):
    if message.text == '🎁 Ввести промокод':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.ENTER_PROMOCODE,
            metadata={'user_id': user_id}
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите промокод, чтобы начать пользоваться ботом',
            parse_mode='MarkdownV2',
            reply_markup=get_back_button_markup()
        )
    elif message.text == '✅ Оформить подписку':
        initiate_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.SUBSCRIBE,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=OFFER_MESSAGE_TEXT.format(price=os.getenv('SUBSCRIPTION_PRICE', 3000)),
            parse_mode='MarkdownV2',
            reply_markup=get_confirm_subscription_markup()
        )
    else:
        send_paywall_message(message)
