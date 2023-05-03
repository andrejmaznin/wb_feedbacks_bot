from logic.auth import internals


def check_cookie(client_id):
    return internals.check_cookie(client_id=client_id)


def initiate_auth_data_update(client_id: str, telegram_id: int) -> None:
    internals.initiate_auth_data_update(client_id=client_id, telegram_id=telegram_id)
