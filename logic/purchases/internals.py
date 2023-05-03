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
