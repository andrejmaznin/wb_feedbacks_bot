import json

from app.connections import get_scan_queue
from libs.ydb import prepare_and_execute_query
from modules.cabinets.schemas import CabinetSchema
from modules.feedbacks.schemas import ScanCabinetTask


def start_bot(client_id: str):
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        '$purchase_id=SELECT id FROM purchases WHERE client_id=$clientId;'
        'UPSERT INTO purchases (id, client_id, execute) '
        'VALUES ($purchase_id, $clientId, True)',
        clientId=client_id
    )
    cabinets = CabinetSchema.get_for_client(client_id=client_id)
    scan_queue = get_scan_queue()
    for cabinet in cabinets:
        scan_queue.send_message(
            MessageBody=ScanCabinetTask(clientId=client_id, cabinetId=cabinet.id).json(by_alias=True)
        )


def stop_bot(client_id: str):
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        '$purchase_id=SELECT id FROM purchases WHERE client_id=$clientId;'
        'UPSERT INTO purchases (id, client_id, execute) '
        'VALUES ($purchase_id, $clientId, False)',
        clientId=client_id
    )
