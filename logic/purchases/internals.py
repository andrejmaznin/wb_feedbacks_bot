from libs.ydb import prepare_and_execute_query


def check_has_purchase(client_id: str) -> bool:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'SELECT id FROM purchases where client_id=$clientId',
        clientId=client_id
    )

    if rows:
        return True
    return False


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
