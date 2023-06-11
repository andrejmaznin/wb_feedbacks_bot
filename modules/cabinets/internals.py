from typing import Dict, List

from connections import bot
from libs.microsoft import get_ms_client
from libs.ydb import prepare_and_execute_query
from modules.cabinets.messages import format_list_of_cabinets
from modules.cabinets.schemas import CabinetSchema
from modules.users.schemas import UserSchema


def get_formatted_list_of_cabinets(client_id: str) -> str:
    cabinets = CabinetSchema.get_for_client(client_id=client_id)
    return format_list_of_cabinets(cabinets=cabinets)


def delete_invalid_cabinets_for_client(client_id: str) -> None:
    ms_client = get_ms_client()

    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'SELECT id, table_id FROM cabinets WHERE client_id=$clientId AND invalid=True;',
        clientId=client_id
    )
    cabinet_ids = [row.id.decode('utf-8') for row in rows]
    table_ids = [row.table_id.decode('utf-8') for row in rows]

    for table_id in table_ids:
        ms_client.delete_item(item_id=table_id)
    prepare_and_execute_query(
        'DECLARE $cabinetIds AS List<String>;'
        'DELETE FROM cabinets WHERE id IN $cabinetIds;'
        'DELETE FROM barcode_feedbacks WHERE cabinet_id IN $cabinetIds;'
        'DELETE FROM brand_feedbacks WHERE cabinet_id IN $cabinetIds;',
        cabinetIds=cabinet_ids
    )


def check_cabinet_exists(client_id: str, title: str) -> bool:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DECLARE $title AS String;'
        'SELECT id FROM cabinets '
        'WHERE client_id=$clientId AND title=$title;',
        clientId=client_id,
        title=title
    )

    if rows:
        return True
    return False


def notify_invalid_cabinet(cabinet: CabinetSchema) -> None:
    users = UserSchema.get_for_client(client_id=cabinet.client_id)
    for user in users:
        if not user.pending:
            bot.send_message(
                chat_id=user.telegram_id,
                text=f'❗️ Пожалуйста\, обновите токен для кабинета `{cabinet.title}`\. Бот не может в нем авторизоваться',
                parse_mode='MarkdownV2'
            )


def get_refresh_messages_for_client(client_id: str) -> List[Dict[str, str]]:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'SELECT id, table_id FROM cabinets WHERE client_id=$clientId;',
        clientId=client_id
    )
    return [
        {
            'cabinetId': row.id.decode('utf-8'),
            'tableId': row.table_id.decode('utf-8')
        } for row in rows
    ]
