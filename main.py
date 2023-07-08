import json
import logging
import os

import telebot
from flask import Flask, request

from app.connections import bot, dispose_connections
from app.settings import settings
from modules.core.dispatch import (dispatch_commands, dispatch_event,
                                   dispatch_purchase_command)
from modules.microsoft import blueprint as microsoft_blueprint
from modules.purchases import check_has_purchase, handle_successful_payment
from modules.purchases.consts import OFFER_TEXT
from modules.users import (activate_invited_user, create_client_and_user,
                           get_user)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(blueprint=microsoft_blueprint, url_prefix='/microsoft')


@app.route('/yookassa', methods=['POST'])
def handle_successful_payment_webhook():
    webhook_body = request.json
    logger.info(webhook_body)
    if webhook_body['event'] == 'payment.succeeded':
        handle_successful_payment(
            payment_id=webhook_body['object'].get('metadata', {}).get('paymentId', ''),
            cabinets_cap=int(webhook_body['object'].get('metadata', {}).get('cabinetsCap', 1))
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


@app.route('/telegram', methods=['GET', 'POST'])
def process_webhook():
    request_body_dict = request.json
    update = telebot.types.Update.de_json(request_body_dict)
    try:
        if request_body_dict.get('message'):
            if user := get_user(
                telegram_id=update.message.from_user.id,
                username=update.message.from_user.username
            ):
                print(f'User: {user}')
                if user.pending is True:
                    activate_invited_user(
                        user_id=user.id,
                        client_id=user.client_id,
                        telegram_id=update.message.from_user.id,
                        username=update.message.from_user.username
                    )
                    return

            else:
                bot.send_message(
                    text=OFFER_TEXT.format(price_1=settings.LOGIC.price_1),
                    chat_id=update.message.from_user.id,
                    parse_mode='MarkdownV2'
                )
                user = create_client_and_user(
                    telegram_id=update.message.from_user.id,
                    username=update.message.from_user.username
                )

            if check_has_purchase(user.client_id):
                if update.message.text or update.message.document:
                    dispatch_commands(update.message, user.client_id)
                bot.process_new_updates([update])
            else:
                if update.message.text:
                    dispatch_purchase_command(
                        message=update.message,
                        client_id=user.client_id,
                        user_id=user.id
                    )
            dispose_connections()

    except Exception as e:
        logger.error(f'Logging error {e}', exc_info=True)
        # raise e

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


@app.route('/', methods=['GET', 'POST'])
def process_trigger():
    request_body_dict = request.json
    if messages := request_body_dict.get('messages'):
        for message in messages:
            dispatch_event(message=message)

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
