import json

from connections.ymq import get_cabinets_queue
from libs.ydb import prepare_and_execute_query
from modules.cabinets.schemas import CabinetSchema


def start_bot(client_id: str):
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        '$purchase_id=SELECT id FROM purchases WHERE client_id=$clientId;'
        'UPSERT INTO purchases (id, client_id, execute) '
        'VALUES ($purchase_id, $clientId, True)',
        clientId=client_id
    )
    cabinets = CabinetSchema.get_for_client(client_id=client_id)
    cabinets_queue = get_cabinets_queue()
    for cabinet in cabinets:
        cabinets_queue.send_message(
            MessageBody=json.dumps({'clientId': client_id, 'cabinetId': cabinet.id})
        )


def stop_bot(client_id: str):
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        '$purchase_id=SELECT id FROM purchases WHERE client_id=$clientId;'
        'UPSERT INTO purchases (id, client_id, execute) '
        'VALUES ($purchase_id, $clientId, False)',
        clientId=client_id
    )
