import os

from connections.boto3 import get_boto_session_async, get_boto_session

reviews_queue = None
reviews_queue_async = None
cabinets_queue = None
cabinets_queue_async = None
refresh_queue = None
refresh_queue_async = None


def get_reviews_queue():
    global reviews_queue
    if reviews_queue is not None:
        return reviews_queue

    reviews_queue = get_boto_session().resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    ).Queue(os.environ['YMQ_REVIEWS_QUEUE_URL'])
    return reviews_queue


async def get_reviews_queue_async():
    global reviews_queue_async
    if reviews_queue_async is not None:
        return reviews_queue_async

    async with get_boto_session_async().resource(
            service_name='sqs',
            endpoint_url='https://message-queue.api.cloud.yandex.net',
            region_name='ru-central1'
    ) as resource:
        reviews_queue_async = await resource.Queue(os.environ['YMQ_REVIEWS_QUEUE_URL'])
    return reviews_queue_async


def get_cabinets_queue():
    global cabinets_queue
    if cabinets_queue is not None:
        return cabinets_queue

    cabinets_queue = get_boto_session().resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    ).Queue(os.environ['YMQ_CABINETS_QUEUE_URL'])
    return cabinets_queue


async def get_cabinets_queue_async():
    global cabinets_queue_async
    if cabinets_queue_async is not None:
        return cabinets_queue_async

    async with get_boto_session_async().resource(
            service_name='sqs',
            endpoint_url='https://message-queue.api.cloud.yandex.net',
            region_name='ru-central1'
    ) as resource:
        cabinets_queue_async = await resource.Queue(os.environ['YMQ_CABINETS_QUEUE_URL'])

    return cabinets_queue_async


def get_refresh_queue():
    global refresh_queue
    if refresh_queue is not None:
        return refresh_queue

    refresh_queue = get_boto_session().resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    ).Queue(os.environ['YMQ_REFRESH_FEEDBACKS_URL'])
    return refresh_queue


async def get_refresh_queue_async():
    global refresh_queue_async
    if refresh_queue_async is not None:
        return refresh_queue_async

    async with get_boto_session_async().resource(
            service_name='sqs',
            endpoint_url='https://message-queue.api.cloud.yandex.net',
            region_name='ru-central1'
    ) as resource:
        refresh_queue_async = await resource.Queue(os.environ['YMQ_REFRESH_FEEDBACKS_QUEUE_URL'])
    return refresh_queue_async
