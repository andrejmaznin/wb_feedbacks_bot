import json
import logging
from typing import Optional

import requests

from connections import get_reviews_queue
from connections.redis import get_redis_client
from connections.ydb import dispose_connections
from connections.ymq import get_cabinets_queue
from modules.wb_bot.cabinets import WB_FEEDBACKS_API_URL
from modules.wb_bot.cabinets import notify_invalid_cabinet
from modules.wb_bot.cabinets import CabinetSchema
from modules.wb_bot.purchases import check_should_execute
from settings import logic_settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def scan_cabinet(cabinet: CabinetSchema, client_id: str) -> Optional[dict]:
    redis_client = get_redis_client()

    response = requests.get(
        url=WB_FEEDBACKS_API_URL,
        headers=cabinet.headers,
        params={
            'take': 100,
            'skip': 0,
            'hasSupplierComplaint': False,
            'isAnswered': False,
            'order': 'dateDesc'
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
    redis_keys = redis_client.mget(
        keys=[
            f'no-feedback:{client_id}:{review["productDetails"]["nmId"]}'
            for review in reviews
        ]
    )
    reviews_needed_info = [
        {
            'id': review['id'],
            'stars': review['productValuation'],
            'barcode': str(review['productDetails']['nmId']),
            'brand': review['productDetails']['brandName'],
            'isCreationSupplierComplaint': review['isCreationSupplierComplaint']
        } for review in reviews
    ]

    messages = []
    for rkey, review in zip(redis_keys, reviews_needed_info):
        if rkey is None:
            if 1 <= review['stars'] <= 3:
                if review['isCreationSupplierComplaint']:
                    messages.append(review)
            else:
                messages.append(review)

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

        if task := scan_cabinet(cabinet=cabinet, client_id=client_id):
            reviews_queue.send_message(MessageBody=json.dumps(task))
            cabinets_queue.send_message(
                MessageBody=json.dumps({'clientId': client_id, 'cabinetId': cabinet_id}),
                DelaySeconds=logic_settings.scan_cabinet_delay
            )
    dispose_connections()
