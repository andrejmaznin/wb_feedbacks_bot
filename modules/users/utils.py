from typing import Optional

from connections import get_session_pool


def is_owner(
    client_id: str,
    telegram_id: int,
    username: Optional[str] = None
) -> bool:
    pool = get_session_pool()

    with pool.checkout() as session:
        if username is not None:
            query = f'SELECT owner FROM users ' \
                    f'WHERE client_id="{client_id}" AND telegram_id="{telegram_id}" AND username="{username}"'
        else:
            query = f'SELECT owner FROM users ' \
                    f'WHERE client_id="{client_id}" AND telegram_id="{telegram_id}"'
        result = session.transaction().execute(query, commit_tx=True)

    if result[0].rows:
        if result[0].rows[0].owner is True:
            return True
    return False
