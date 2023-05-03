from typing import List

from logic.users.schemas import UserSchema


def format_list_of_users(users: List[UserSchema]) -> str:
    users_text = 'Вот список пользователей, связанных с вашим аккаунтом:\n'
    invited_text = 'Приглашенные пользователи:\n'
    invited_list = []

    for counter, user in enumerate(users, start=1):
        if user.pending is True:
            invited_list.append(f'`{user.data}`')
        else:
            telegram_id = user.telegram_id
            if user.username:
                username = user.username
                users_text += f'*{counter}*\. ID: `{telegram_id}`, username: `@{username}`\n'
            else:
                users_text += f'*{counter}*\. ID: `{telegram_id}`\n'

    if invited_list := list(set(invited_list)):
        return users_text + '\n' + invited_text + ', '.join(invited_list)

    return users_text + '\n' + 'Приглашенных пользователей нет'
