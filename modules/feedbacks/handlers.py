import json
from typing import Dict

from connections import get_reviews_queue
from connections.ymq import get_cabinets_queue
from libs.microsoft import get_ms_client
from libs.wildberries.exceptions import WBAuthException
from modules.cabinets import notify_invalid_cabinet
from modules.cabinets.schemas import CabinetSchema
from modules.feedbacks.internals.excel import import_feedbacks_from_table
from modules.feedbacks.internals.wildberries import scan_cabinet, reply_for_cabinet
from modules.feedbacks.schemas import ScanCabinetTask, ReplyCabinetTask, ReplySettingsSchema, UpdateFeedbacksTask
from modules.purchases import check_should_execute
from settings import logic_settings


def scan_cabinet_handler(message: Dict) -> None:
    reviews_queue = get_reviews_queue()
    cabinets_queue = get_cabinets_queue()

    task = ScanCabinetTask.parse_obj(json.loads(message['details']['message']['body']))
    cabinet = CabinetSchema.get_by_id(id=task.cabinet_id)
    if not check_should_execute(client_id=task.client_id) or cabinet.invalid:
        return

    try:
        reviews = scan_cabinet(cabinet=cabinet, client_id=task.client_id)
    except WBAuthException:
        cabinet.mark_as_invalid()
        notify_invalid_cabinet(cabinet=cabinet)
        return

    reviews_queue.send_message(
        MessageBody=ReplyCabinetTask(
            clientId=task.client_id,
            cabinetId=task.cabinet_id,
            reviews=reviews
        ).json(by_alias=True)
    )
    cabinets_queue.send_message(
        MessageBody=task.json(by_alias=True),
        DelaySeconds=logic_settings.scan_cabinet_delay
    )


async def reply_cabinet_handler(message: Dict) -> None:
    task = ReplyCabinetTask.parse_obj(json.loads(message['details']['message']['body']))
    settings = await ReplySettingsSchema.get_for_client_async(client_id=task.client_id)
    await reply_for_cabinet(
        client_id=task.client_id,
        cabinet_id=task.cabinet_id,
        reviews=task.reviews,
        settings=settings
    )


def update_feedbacks_handler(message: Dict) -> None:
    ms_client = get_ms_client()

    task = UpdateFeedbacksTask.parse_obj(json.loads(message['details']['message']['body']))
    table_content = ms_client.download_item_content(item_id=task.table_id)
    import_feedbacks_from_table(table_content=table_content, cabinet_id=task.cabinet_id)
