import json
import uuid

from app.connections import get_scan_queue
from libs.ydb.utils import prepare_and_execute_query_async


async def get_cabinets_purchases_page(limit: int, offset: int = 0):
    rows = await prepare_and_execute_query_async(
        'DECLARE $limit AS Uint64;'
        'DECLARE $offset AS Uint64;'
        'SELECT cabinets.client_id AS client_id, cabinets.id AS id FROM cabinets '
        'INNER JOIN purchases ON cabinets.client_id = purchases.client_id '
        'WHERE execute=True AND invalid<>True '
        'LIMIT $limit OFFSET $offset',
        limit=limit,
        offset=offset
    )
    return rows


async def paginate_cabinets_purchases(limit: int = 10):
    offset = 0
    while True:
        results = await get_cabinets_purchases_page(limit=limit, offset=offset)
        if not results:
            return

        offset += limit

        group_id = str(uuid.uuid4())
        yield [
            {
                'Id': str(uuid.uuid4()),
                'MessageBody': json.dumps({
                    'clientId': result.client_id.decode('utf-8'),
                    'cabinetId': result.id.decode('utf-8')
                }),
                'MessageGroupId': group_id
            } for result in results
        ]


async def handle_all_cabinets():
    scan_queue = get_scan_queue()

    async for cabinets in paginate_cabinets_purchases(limit=10):
        scan_queue.send_messages(Entries=cabinets)


async def handler(event, context):
    await handle_all_cabinets()
