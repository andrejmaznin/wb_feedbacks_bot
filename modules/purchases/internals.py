import uuid

from connections import bot
from libs.ydb import prepare_and_execute_query
from modules.wb_bot.markups.root import get_root_reply_markup
from modules.users.schemas import UserSchema


def check_has_purchase(client_id: str) -> bool:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'SELECT id FROM purchases where client_id=$clientId',
        clientId=client_id
    )
    return True if rows else False


def check_should_execute(client_id: str) -> bool:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'SELECT id, execute FROM purchases where client_id=$clientId',
        clientId=client_id
    )

    if rows:
        if rows[0].execute:
            return True
    return False


def handle_successful_payment(payment_id: str) -> None:
    rows = prepare_and_execute_query(
        'DECLARE $paymentId AS String;'
        'SELECT client_id, telegram_id FROM payments WHERE id=$paymentId',
        paymentId=payment_id
    )
    if not rows:
        return
    client_id = rows[0].client_id.decode('utf-8')
    telegram_id = rows[0].telegram_id.decode('utf-8')
    user = UserSchema.get_by_telegram_id(telegram_id=telegram_id)

    prepare_and_execute_query(
        'DECLARE $paymentId AS String;'
        'DECLARE $clientId AS String;'
        'DECLARE $telegramId AS String;'
        'DECLARE $purchaseId AS String;'
        'DECLARE $userId AS String;'
        'DECLARE $settingsId AS String;'
        'DELETE FROM payments WHERE id=$paymentId;'
        'DELETE FROM commands WHERE client_id=$clientId AND telegram_id=$telegramId;'
        'UPSERT INTO purchases (id, client_id, date, execute) VALUES ($purchaseId, $clientId, CurrentUtcDate(), False);'
        'UPSERT INTO settings (id, client_id, complain) VALUES ($settingsId, $clientId, False);'
        'UPSERT INTO users (id, owner) VALUES ($userId, True)',
        paymentId=payment_id,
        clientId=client_id,
        telegramId=telegram_id,
        purchaseId=str(uuid.uuid4()),
        settingsId=str(uuid.uuid4()),
        userId=user.id
    )

    bot.send_message(
        chat_id=int(telegram_id),
        text='✅ Поздравляем, бот готов к работе\!',
        parse_mode='MarkdownV2',
        reply_markup=get_root_reply_markup(client_id)
    )
