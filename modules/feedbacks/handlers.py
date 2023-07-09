import json
import logging
from typing import Dict

from app.connections import get_reply_queue, get_scan_queue
from app.settings import settings
from libs.microsoft import get_ms_client
from libs.wildberries.exceptions import WBAuthException
from modules.cabinets import notify_invalid_cabinet
from modules.cabinets.schemas import CabinetSchema
from modules.feedbacks.internals.excel import import_feedbacks_from_table
from modules.feedbacks.internals.wildberries import (reply_for_cabinet,
                                                     scan_cabinet)
from modules.feedbacks.schemas import (ReplyCabinetTask, ReplySettingsSchema,
                                       ScanCabinetTask, UpdateFeedbacksTask)
from modules.purchases import check_should_execute

logger = logging.getLogger(__name__)


def scan_cabinet_handler(message: Dict) -> None:
    try:
        reviews_queue = get_reply_queue()
        scan_queue = get_scan_queue()

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
        scan_queue.send_message(
            MessageBody=task.json(by_alias=True),
            DelaySeconds=settings.LOGIC.scan_delay
        )

    except Exception as e:
        logger.error(f'Error while scanning cabinet {e}', exc_info=True)
        raise e


async def reply_cabinet_handler(message: Dict) -> None:
    try:
        task = ReplyCabinetTask.parse_obj(json.loads(message['details']['message']['body']))
        settings = await ReplySettingsSchema.get_for_client_async(client_id=task.client_id)
        await reply_for_cabinet(
            client_id=task.client_id,
            cabinet_id=task.cabinet_id,
            reviews=task.reviews,
            settings=settings
        )

    except Exception as e:
        logger.error(f'Error while replying to feedbacks {e}', exc_info=True)
        raise e


def update_feedbacks_handler(message: Dict) -> None:
    ms_client = get_ms_client()

    task = UpdateFeedbacksTask.parse_obj(json.loads(message['details']['message']['body']))
    table_content = ms_client.download_item_content(item_id=task.table_id)
    import_feedbacks_from_table(table_content=table_content, cabinet_id=task.cabinet_id)
