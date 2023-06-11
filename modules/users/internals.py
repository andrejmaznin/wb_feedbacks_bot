import uuid
from typing import Optional

from connections import bot, get_session_pool
from libs.ydb import get_or_generate_id, prepare_and_execute_query
from modules.users.schemas import UserSchema
from modules.wb_bot.markups.root import get_root_reply_markup
from modules.wb_bot.users.messages import format_list_of_users


def add_user(client_id: str, data: str):
    pool = get_session_pool()

    data = data.lstrip('@')
    user_id = get_or_generate_id(
        f'SELECT id FROM users '
        f'WHERE (data="{data}" OR username="{data}" OR telegram_id="{data}") '
        f'AND client_id="{client_id}"'
    )

    with pool.checkout() as session:
        session.transaction().execute(
            f'UPSERT INTO users (id, client_id, pending, data) '
            f'VALUES ("{user_id}", "{client_id}", True, "{data}")',
            commit_tx=True
        )


def activate_invited_user(
    client_id: str,
    user_id: str,
    telegram_id: int,
    username: Optional[str] = None
):
    pool = get_session_pool()

    with pool.checkout() as session:
        if username is not None:
            username = username.lstrip('@')
            query = f'UPDATE users SET pending=False, data=NULL, owner=False, ' \
                    f'telegram_id="{telegram_id}", username="{username}" ' \
                    f'WHERE id="{user_id}" AND client_id="{client_id}"'
        else:
            query = f'UPDATE users SET pending=False, data=NULL, owner=False' \
                    f'telegram_id="{telegram_id}" ' \
                    f'WHERE id="{user_id}" AND client_id="{client_id}"'

        session.transaction().execute(query, commit_tx=True)

    bot.send_message(
        chat_id=telegram_id,
        text='Добро пожаловать!\nВы были приглашены другим участником',
        reply_markup=get_root_reply_markup(client_id)
    )


def delete_user(
    client_id: str,
    data: str,
    telegram_id: int,
    username: Optional[str] = None
) -> bool:
    pool = get_session_pool()

    if data == str(telegram_id) or data == username:
        return False

    with pool.checkout() as session:
        result = session.transaction().execute(
            f'SELECT id FROM users '
            f'WHERE client_id="{client_id}" AND (telegram_id="{data}" OR username="{data}" OR data="{data}")',
            commit_tx=True
        )
        if not result[0].rows:
            return False

        user_id = result[0].rows[0].id.decode('utf-8')
        session.transaction().execute(
            f'DELETE FROM users WHERE id="{user_id}"',
            commit_tx=True
        )

    return True


def get_user(
    telegram_id: int,
    username: Optional[str] = None
) -> Optional[UserSchema]:
    if username is not None:
        rows = prepare_and_execute_query(
            'DECLARE $telegramId AS String;'
            'DECLARE $username AS String;'
            'SELECT * FROM users WHERE telegram_id=$telegramId AND username=$username AND pending=False',
            telegramId=str(telegram_id),
            username=username
        )
    else:
        rows = prepare_and_execute_query(
            'DECLARE $telegramId AS String;'
            'SELECT * FROM users WHERE telegram_id=$telegramId AND pending=False',
            telegramId=str(telegram_id),
        )

    if not rows:
        if username is not None:
            rows = prepare_and_execute_query(
                'DECLARE $telegramId AS String;'
                'DECLARE $username AS String;'
                'SELECT * FROM users WHERE (data=$telegramId or data=$username) AND pending=True',
                telegramId=str(telegram_id),
                username=username
            )
        else:
            rows = prepare_and_execute_query(
                'DECLARE $telegramId AS String;'
                'DECLARE $username AS String;'
                'SELECT * FROM users WHERE data=$telegramId AND pending=True',
                telegramId=str(telegram_id),
            )

    if not rows:
        return None

    return UserSchema(
        id=rows[0].id.decode('utf-8'),
        client_id=rows[0].client_id.decode('utf-8'),
        username=username,
        telegram_id=telegram_id,
        data=rows[0].data.decode('utf-8') if rows[0].data is not None else None,
        owner=rows[0].owner,
        pending=rows[0].pending
    )


def get_formatted_list_of_users(client_id: str) -> str:
    users = UserSchema.get_for_client(client_id=client_id)
    return format_list_of_users(users=users)


def create_client_and_user(
    telegram_id: int,
    username: Optional[str] = None
) -> UserSchema:
    pool = get_session_pool()

    client_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    with pool.checkout() as session:
        session.transaction().execute(
            f'UPSERT INTO clients (id) VALUES ("{client_id}")',
            commit_tx=True
        )
        if username is not None:
            session.transaction().execute(
                f'UPSERT INTO users (id, client_id, telegram_id, username, pending) VALUES '
                f'("{user_id}", "{client_id}", "{telegram_id}", "{username}", False)',
                commit_tx=True
            )
        else:
            session.transaction().execute(
                f'UPSERT INTO users (id, client_id, telegram_id, pending) VALUES '
                f'("{user_id}", "{client_id}", "{telegram_id}", False)',
                commit_tx=True
            )

    return UserSchema(
        id=user_id,
        client_id=client_id,
        telegram_id=telegram_id,
        username=username,
        pending=False
    )


def authorize_user(
    telegram_id: int,
    username: Optional[str] = None
) -> Optional[UserSchema]:
    if user := get_user(telegram_id=telegram_id, username=username):
        print(f'User: {user}')
        if user.pending is True:
            activate_invited_user(
                user_id=user.id,
                client_id=user.client_id,
                telegram_id=telegram_id,
                username=username
            )
        return user
    return None
