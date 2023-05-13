import json
import logging
from typing import Optional

import requests

from connections import get_reviews_queue
from connections.ymq import get_cabinets_queue
from logic.cabinets.consts import WB_FEEDBACKS_API_URL
from logic.cabinets.internals import notify_invalid_cabinet
from logic.cabinets.schemas import CabinetSchema
from logic.purchases.exports import check_should_execute

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def scan_cabinet(cabinet: CabinetSchema) -> Optional[dict]:
    response = requests.get(
        url=WB_FEEDBACKS_API_URL,
        headers=cabinet.headers,
        params={
            'take': 100,
            'skip': 0,
            'hasSupplierComplaint': False,
            'isAnswered': False,
            'order': 'dateDesc',
        }
    )

    data = response.json() if 200 <= response.status_code < 300 else None
    if not data or not data.get('data'):
        logger.error(response.text)
        if response.status_code in (400, 401, 403):
            logger.error(response.text)
            cabinet.mark_as_invalid()
            notify_invalid_cabinet(cabinet=cabinet)
            return

    reviews = data['data']['feedbacks']
    messages = [
        {
            'id': review['id'],
            'stars': review['productValuation'],
            'text': review['text'],
            'barcode': str(review['productDetails']['nmId']),
            'brand': review['productDetails']['brandName']
        } for review in reviews
    ]

    return {
        'clientId': cabinet.client_id,
        'cabinetId': cabinet.id,
        'reviews': messages
    }


def handler(event, context):
    reviews_queue = get_reviews_queue()
    cabinets_queue = get_cabinets_queue()

    for message in event['messages']:

        task_body = json.loads(message['details']['message']['body'])
        cabinet_id = task_body['cabinetId']
        client_id = task_body['clientId']
        cabinet = CabinetSchema.get_by_id(id=cabinet_id)

        if not check_should_execute(client_id=client_id) or cabinet.invalid:
            return

        if task := scan_cabinet(cabinet=cabinet):
            reviews_queue.send_message(MessageBody=json.dumps(task))
            cabinets_queue.send_message(
                MessageBody=json.dumps({'clientId': client_id, 'cabinetId': cabinet_id}),
                DelaySeconds=300
            )
