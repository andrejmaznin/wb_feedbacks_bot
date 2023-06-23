from typing import Optional, Union

from app.connections import bot
from modules.commands import Commands, finish_command
from modules.purchases.consts import PLANS_CAPS_MAP, PLANS_PRICES_MAP
from modules.purchases.exports import create_payment
from modules.wb_bot.markups.purchases import get_purchase_markup
from modules.wb_bot.purchases.messages import get_payment_url_message_text


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[list, dict]] = None
):
    text = message.text
    if text == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.SUBSCRIBE,
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_purchase_markup(),
            parse_mode='MarkdownV2'
        )
        return

    if metadata['step'] == 'plans':
        if amount := PLANS_PRICES_MAP.get(text):
            confirmation_url = create_payment(
                client_id=client_id,
                telegram_id=message.from_user.id,
                amount=amount,
                cabinets_cap=PLANS_CAPS_MAP.get(text, 1)
            )
            bot.send_message(
                chat_id=message.from_user.id,
                text=get_payment_url_message_text(confirmation_url=confirmation_url),
            )
        else:
            bot.send_message(
                chat_id=message.from_user.id,
                text='Не поняли вас',
                parse_mode='MarkdownV2'
            )
