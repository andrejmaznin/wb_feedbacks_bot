import json
import logging
import os

import telebot
from flask import Flask, request

from connections import bot
from connections.ydb import dispose_connections
from modules.core.dispatch import dispatch_purchase_command, dispatch_commands, dispatch_event
from modules.microsoft import blueprint as microsoft_blueprint
from modules.purchases import handle_successful_payment, check_has_purchase
from modules.users.exports import authorize_user, create_client_and_user

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(blueprint=microsoft_blueprint, url_prefix='/microsoft')


@app.route('/yookassa', methods=['POST'])
def handle_successful_payment_webhook():
    webhook_body = request.json
    if webhook_body['event'] == 'payment.succeeded':
        handle_successful_payment(webhook_body['object'].get('metadata', {}).get('paymentId', ''))

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
            user = authorize_user(
                telegram_id=update.message.from_user.id,
                username=update.message.from_user.username
            )
            if user is None:
                user = create_client_and_user(
                    telegram_id=update.message.from_user.id,
                    username=update.message.from_user.username
                )
                client_id = user.client_id
            else:
                client_id = user.client_id
            if check_has_purchase(client_id):
                if update.message.text or update.message.document:
                    dispatch_commands(update.message, client_id)
                bot.process_new_updates([update])
            else:
                if update.message.text:
                    dispatch_purchase_command(
                        message=update.message,
                        client_id=client_id,
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


# temporarily only for events
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
