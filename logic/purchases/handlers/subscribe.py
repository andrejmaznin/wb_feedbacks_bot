import os
import uuid
from typing import Optional, Union

from yookassa import Payment

from commands import Commands, finish_command
from connections import bot, config_yookassa
from libs.ydb import prepare_and_execute_query
from logic.purchases.messages import get_payment_url_message_text
from markups.purchases import get_confirm_subscription_markup, get_purchase_markup


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
            parse_mode='MarkdownV2',
            reply_markup=get_purchase_markup()
        )

    if text == '💰 Оплата':
        config_yookassa()
        payment_id = str(uuid.uuid4())
        payment = Payment.create({
            'amount': {
                'value': f'{os.getenv("SUBSCRIPTION_PRICE", 3000)}.00',
                'currency': 'RUB'
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': 'https://t.me/otzyvywbbot'
            },
            'metadata': {
                'paymentId': payment_id
            },
            'receipt': {
                'customer': {
                    'full_name': 'Мазнин Андрей Дмитриевич',
                    'inn': '744515727712',
                    'email': 'andrejmaznin@gmail.com'
                },
                'items': [
                    {
                        'description': 'Месяц подписки на бота otzyvywbbot',
                        'amount': {
                            'value': '10.00',
                            'currency': 'RUB'
                        },
                        'vat_code': 1,
                        'quantity': '1',
                        'payment_subject': 'service',
                        'payment_mode': 'full_payment',
                        'country_of_origin_code': 'RU'
                    }
                ]
            },
            'capture': True,
            'description': 'Оплата подписки'
        }, payment_id)

        prepare_and_execute_query(
            'DECLARE $paymentId AS String;'
            'DECLARE $clientId AS String;'
            'DECLARE $telegramId AS String;'
            'UPSERT INTO payments (id, client_id, telegram_id) VALUES ($paymentId, $clientId, $telegramId)',
            paymentId=payment_id,
            clientId=client_id,
            telegramId=str(message.from_user.id)
        )

        bot.send_message(
            chat_id=message.from_user.id,
            text=get_payment_url_message_text(confirmation_url=payment.confirmation.confirmation_url),
            reply_markup=get_confirm_subscription_markup()
        )
