from connections import bot
from markups.purchases import get_purchase_markup


def send_paywall_message(message):
    bot.send_message(
        message.from_user.id,
        'Оформите подписку, чтобы пользоваться функционалом бота',
        reply_markup=get_purchase_markup()
    )


def get_payment_url_message_text(confirmation_url: str) -> str:
    title_text = 'Вот ваша ссылка на оплату:'
    bottom_text = 'Как только оплата успешно завершится, вы получите сообщение'
    return f'{title_text}\n\n{confirmation_url}\n\n{bottom_text}'
