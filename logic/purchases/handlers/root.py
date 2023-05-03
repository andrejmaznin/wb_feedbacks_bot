from commands import initiate_command, Commands
from connections import bot
from markups.common import get_back_button_markup
from logic.purchases.messages import send_offer_message, send_paywall_message


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
    elif message.text == '💰 Оформить подписку':
        send_offer_message(message)
    else:
        send_paywall_message(message)
