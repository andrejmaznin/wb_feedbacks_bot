from app.connections.boto3 import get_boto_session, get_boto_session_async
from app.settings import settings

reply_queue = None
reply_queue_async = None
scan_queue = None
scan_queue_async = None
update_queue = None
update_queue_async = None


def get_queue(url: str):
    return get_boto_session().resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    ).Queue(url)


async def get_queue_async(url: str):
    async with get_boto_session_async().resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    ) as resource:
        queue = await resource.Queue(url)
    return queue


def get_reply_queue():
    global reply_queue
    if reply_queue is not None:
        return reply_queue

    reply_queue = get_queue(settings.YMQ.reply_url)
    return reply_queue


async def get_reply_queue_async():
    global reply_queue_async
    if reply_queue_async is not None:
        return reply_queue_async

    reply_queue_async = await get_queue_async(settings.YMQ.reply_url)
    return reply_queue_async


def get_scan_queue():
    global scan_queue
    if scan_queue is not None:
        return scan_queue

    scan_queue = get_queue(settings.YMQ.scan_url)
    return scan_queue


async def get_scan_queue_async():
    global scan_queue_async
    if scan_queue_async is not None:
        return scan_queue_async

    scan_queue_async = await get_queue_async(settings.YMQ.scan_url)
    return scan_queue_async


def get_update_queue():
    global update_queue
    if update_queue is not None:
        return update_queue

    update_queue = get_queue(settings.YMQ.update_url)
    return update_queue


async def get_update_queue_async():
    global update_queue_async
    if update_queue_async is not None:
        return update_queue_async

    update_queue_async = await get_queue_async(settings.YMQ.update_url)
    return update_queue_async
