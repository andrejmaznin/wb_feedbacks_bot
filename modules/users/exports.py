from typing import Optional

from modules.users import internals
from modules.users.schemas import UserSchema


def get_user(
    telegram_id: int,
    username: Optional[str] = None
) -> Optional[UserSchema]:
    return internals.get_user(telegram_id=telegram_id, username=username)


def activate_invited_user(
    client_id: str,
    user_id: str,
    telegram_id: int,
    username: Optional[str] = None
) -> None:
    return internals.activate_invited_user(
        client_id=client_id,
        user_id=user_id,
        telegram_id=telegram_id,
        username=username
    )


def create_client_and_user(
    telegram_id: int,
    username: Optional[str] = None
) -> UserSchema:
    return internals.create_client_and_user(telegram_id=telegram_id, username=username)


def get_formatted_list_of_users(client_id: str) -> str:
    return internals.get_formatted_list_of_users(client_id=client_id)


def delete_user(
    client_id: str,
    data: str,
    telegram_id: int,
    username: Optional[str] = None
) -> bool:
    return internals.delete_user(client_id=client_id, data=data, telegram_id=telegram_id, username=username)


def invite_user(client_id: str, data: str) -> None:
    return internals.invite_user(client_id=client_id, data=data)
