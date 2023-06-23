from app.connections import bot
from app.settings import settings
from modules.commands import Commands, initiate_command
from modules.purchases.consts import SUBSCRIPTION_PLANS_TEXT
from modules.wb_bot.markups.common import get_back_button_markup
from modules.wb_bot.markups.purchases import get_subscription_plans_markup
from modules.wb_bot.purchases.messages import send_paywall_message


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
            metadata={'step': 'plans'}
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=SUBSCRIPTION_PLANS_TEXT.format(
                price_1=settings.LOGIC.price_1,
                price_3=settings.LOGIC.price_3,
                price_5=settings.LOGIC.price_5
            ),
            reply_markup=get_subscription_plans_markup(),
            parse_mode='MarkdownV2'
        )
    else:
        send_paywall_message(message)
