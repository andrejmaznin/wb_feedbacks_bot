from connections import bot
from .consts import OFFER_MESSAGE_TEXT
from markups.purchases import get_purchase_markup


def send_paywall_message(message):
    bot.send_message(
        message.from_user.id,
        'Оформите подписку, чтобы пользоваться функционалом бота',
        reply_markup=get_purchase_markup()
    )


def send_offer_message(message):
    bot.send_message(
        chat_id=message.from_user.id,
        text=OFFER_MESSAGE_TEXT,
        parse_mode='MarkdownV2'
    )
