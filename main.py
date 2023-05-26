import json
import logging
import os

import telebot
from flask import Flask, request

from commands.exports import get_user_command_and_metadata
from connections import bot
from connections.ydb import dispose_connections
from logic.auth import handle_update_auth_data_command
from logic.auth.exports import initiate_auth_data_update, check_cookie
from logic.cabinets import handle_cabinets_command, handle_cabinets_add_command, handle_cabinets_remove_command
from logic.feedbacks import handle_feedbacks_command, handle_feedbacks_add_barcode_command, \
    handle_feedbacks_add_text_command, handle_feedbacks_file_import_command, \
    handle_feedbacks_exclude_command, handle_feedbacks_default_command, handle_feedbacks_default_add_command, \
    handle_feedbacks_default_remove_command
from logic.onboarding import handle_user_onboarding_command
from logic.purchases import handle_purchase_command, handle_enter_promocode_purchase_command, \
    handle_subscribe_purchase_command
from logic.purchases.exports import check_has_purchase, handle_successful_payment
from logic.root import handle_root_command
from logic.users import handle_users_command, handle_users_add_command, \
    handle_users_remove_command
from logic.users.exports import authorize_user, create_client_and_user
from services.refresh_ms_token.main import blueprint as microsoft_blueprint

logger = logging.getLogger()

COMMAND_FUNCTION_MAP = {
    'users': handle_users_command,
    'users_add': handle_users_add_command,
    'users_remove': handle_users_remove_command,
    'feedbacks': handle_feedbacks_command,
    'feedbacks_add_barcode': handle_feedbacks_add_barcode_command,
    'feedbacks_add_text': handle_feedbacks_add_text_command,
    'feedbacks_file_import': handle_feedbacks_file_import_command,
    'feedbacks_exclude': handle_feedbacks_exclude_command,
    'feedbacks_default': handle_feedbacks_default_command,
    'feedbacks_default_add': handle_feedbacks_default_add_command,
    'feedbacks_default_remove': handle_feedbacks_default_remove_command,
    'user_onboarding': handle_user_onboarding_command,
    'update_auth_data': handle_update_auth_data_command,
    'cabinets': handle_cabinets_command,
    'cabinets_add': handle_cabinets_add_command,
    'cabinets_remove': handle_cabinets_remove_command
}

PURCHASE_COMMAND_FUNCTION_MAP = {
    'enter_promocode': handle_enter_promocode_purchase_command,
    'subscribe': handle_subscribe_purchase_command
}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Hello!')


def dispatch_commands(message, client_id: str):
    command, metadata = get_user_command_and_metadata(client_id=client_id, telegram_id=message.from_user.id)
    if command is not None:
        command_func = COMMAND_FUNCTION_MAP.get(command)
        command_func(message, client_id, metadata)
    else:
        if not check_cookie(client_id):
            initiate_auth_data_update(client_id=client_id, telegram_id=message.from_user.id)
        else:
            handle_root_command(message, client_id)


def dispatch_purchase_command(message, client_id: str, user_id: str):
    command, metadata = get_user_command_and_metadata(client_id=client_id, telegram_id=message.from_user.id)
    if command is not None:
        purchase_command_func = PURCHASE_COMMAND_FUNCTION_MAP.get(command)
        purchase_command_func(message, client_id, metadata)
    else:
        handle_purchase_command(message=message, client_id=client_id, user_id=user_id)


app = Flask(__name__)
app.register_blueprint(blueprint=microsoft_blueprint, url_prefix='/microsoft')


@app.route('/hello')
def hello():
    return json.dumps('Hello!')


@app.route('/yookassa', methods=['POST'])
def handle_successful_payment_webhook():
    webhook_body = request.json
    if webhook_body['event'] == 'payment.succeeded':
        handle_successful_payment(webhook_body['object'].get('metadata', {}).get('paymentId', ''))

    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                'success': True,
            }
        )
    }


@app.route('/', methods=['GET', 'POST'])
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
        'body': json.dumps(
            {
                'success': True,
            }
        )
    }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
