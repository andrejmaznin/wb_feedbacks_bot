from libs.ydb import prepare_and_execute_query


def start_bot(client_id: str):
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        '$purchase_id=SELECT id FROM purchases WHERE client_id=$clientId;'
        'UPSERT INTO purchases (id, client_id, execute) '
        'VALUES ($purchase_id, $clientId, True)',
        clientId=client_id
    )


def stop_bot(client_id: str):
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        '$purchase_id=SELECT id FROM purchases WHERE client_id=$clientId;'
        'UPSERT INTO purchases (id, client_id, execute) '
        'VALUES ($purchase_id, $clientId, False)',
        clientId=client_id
    )
