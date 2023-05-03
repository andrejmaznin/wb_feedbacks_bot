from typing import Optional

from logic.users import internals
from logic.users.schemas import UserSchema


def authorize_user(
    telegram_id: int,
    username: Optional[str] = None
) -> Optional[UserSchema]:
    return internals.authorize_user(telegram_id=telegram_id, username=username)


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
