from connections import bot
from libs.ydb import prepare_and_execute_query
from logic.cabinets.messages import format_list_of_cabinets
from logic.cabinets.schemas import CabinetSchema
from logic.users.schemas import UserSchema


def get_formatted_list_of_cabinets(client_id: str) -> str:
    cabinets = CabinetSchema.get_for_client(client_id=client_id)
    return format_list_of_cabinets(cabinets=cabinets)


def delete_invalid_cabinets_for_client(client_id: str) -> None:
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DELETE FROM cabinets WHERE client_id=$clientId AND invalid=True;',
        clientId=client_id
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
            bot.send_message(
                chat_id=user.telegram_id,
                text=get_formatted_list_of_cabinets(client_id=cabinet.client_id),
                parse_mode='MarkdownV2'
            )
