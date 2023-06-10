import json
import logging

from connections.ydb import dispose_connections
from libs.microsoft import get_ms_client
from modules.wb_bot.feedbacks.exports import import_feedbacks_from_table

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_feedbacks_from_table(cabinet_id: str, table_id: str):
    ms_client = get_ms_client()
    table_content = ms_client.download_item_content(item_id=table_id)
    import_feedbacks_from_table(table_content=table_content, cabinet_id=cabinet_id)


def handler(event, context):
    for message in event['messages']:
        task_body = json.loads(message['details']['message']['body'])
        cabinet_id = task_body['cabinetId']
        table_id = task_body['tableId']
        update_feedbacks_from_table(cabinet_id=cabinet_id, table_id=table_id)

    dispose_connections()
