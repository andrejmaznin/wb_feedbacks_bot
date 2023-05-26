import json
import logging
from asyncio import gather
from random import choice
from typing import Optional, List

import aiohttp
from redis.asyncio.client import Pipeline

from connections.redis import get_redis_client_async
from connections.ydb import dispose_connections_async
from libs.ydb.utils import prepare_and_execute_query_async
from logic.cabinets.consts import WB_FEEDBACKS_API_URL
from logic.cabinets.schemas import CabinetSchema
from logic.feedbacks.schemas import ReviewSchema, SettingsSchema

logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def get_positive_feedback_text(client_id: str, review: ReviewSchema) -> Optional[str]:
    rows = await prepare_and_execute_query_async(
        'DECLARE $clientId AS String;'
        'DECLARE $barcode AS String;'
        'SELECT pos_feedback FROM barcode_feedbacks '
        'WHERE client_id=$clientId AND barcode=$barcode;',
        clientId=client_id,
        barcode=review.barcode
    )

    if not rows:
        rows = await prepare_and_execute_query_async(
            'DECLARE $clientId AS String;'
            'DECLARE $brand AS String;'
            'SELECT pos_feedback, created_at FROM feedbacks WHERE client_id=$clientId AND '
            'JSON_EXISTS(brands, \'$ ? (@ == $brand)\') '
            'ORDER BY created_at DESC LIMIT 1',
            clientId=client_id,
            brand=review.brand
        )

    if not rows:
        rows = await prepare_and_execute_query_async(
            'DECLARE $clientId AS String;'
            'SELECT pos_feedback FROM feedbacks '
            'WHERE client_id=$clientId AND neg_feedback IS NULL AND barcode IS NULL AND brands IS NULL',
            clientId=client_id
        )

    feedback_text = choice(rows).pos_feedback.decode('utf-8') if rows else None
    return feedback_text


async def get_negative_feedback_text(client_id: str) -> Optional[str]:
    rows = await prepare_and_execute_query_async(
        'DECLARE $clientId AS String;'
        'SELECT neg_feedback FROM feedbacks '
        'WHERE client_id=$clientId AND pos_feedback IS NULL AND barcode IS NULL AND brands IS NULL',
        clientId=client_id
    )
    if rows:
        feedback_text = choice(rows).neg_feedback.decode('utf-8')
        return feedback_text
    return None


async def complain_on_review(
    review_id: str,
    cabinet: CabinetSchema
) -> None:
    body = {
        'id': review_id,
        'createSupplierComplaint': True
    }

    async with aiohttp.ClientSession() as web_session:
        async with web_session.patch(
            url=WB_FEEDBACKS_API_URL,
            headers=cabinet.headers,
            json=body
        ) as response:
            if response.status in (401, 403):
                await cabinet.mark_as_invalid_async()
                return

            data = await response.json()

    if data['error'] is True:
        logger.error(
            f'Error while complaining on review: error: {data["errorText"]}, cabinet:{cabinet.id}, body:{body}'
        )

    # await asyncio.to_thread(bot.send_message, chat_id=452196443, text=f'Complained on review {review_id}')


async def view_review(
    review_id: str,
    cabinet: CabinetSchema,
    web_session: aiohttp.ClientSession
) -> None:
    body = {
        'id': review_id,
        'wasViewed': True
    }
    async with web_session.patch(
        url=WB_FEEDBACKS_API_URL,
        headers=cabinet.headers,
        json=body,
    ) as response:
        if response.status in (401, 403):
            await cabinet.mark_as_invalid_async()
            return

        data = await response.json()

    if data['error'] is True:
        logger.error(
            f'Error while viewing review: error: {data["errorText"]}, cabinet:{cabinet.id}, body:{body}'
        )


async def reply_to_review(
    review_id: str,
    text: str,
    stars: int,
    barcode: str,
    cabinet: CabinetSchema,
    web_session: aiohttp.ClientSession,
):
    body = {
        'id': review_id,
        'text': text
    }

    async with web_session.patch(
        url=WB_FEEDBACKS_API_URL,
        headers=cabinet.headers,
        json=body
    ) as response:
        if response.status in (401, 403):
            await cabinet.mark_as_invalid_async()
            return

        data = await response.json()

    if data['error'] is True:
        logger.error(
            f'Error while answering review: error: {data["errorText"]}, '
            f'cabinet:{cabinet.id}, body:{body}'
        )
    '''

    bot.send_message(
        chat_id=452196443,
        text=f'Answered review {review_id}, barcode: {barcode}, stars: {stars}, answer: {text}'
    )
    '''


async def handle_review(
    client_id: str,
    review: ReviewSchema,
    cabinet: CabinetSchema,
    settings: SettingsSchema,
    web_session: aiohttp.ClientSession,
    redis_pipe: Pipeline
) -> None:
    #  await view_review(review_id=review.id, cabinet=cabinet, web_session=web_session)

    if review.stars in [0, 4, 5]:
        feedback_text = await get_positive_feedback_text(client_id=client_id, review=review)

        if feedback_text is not None:
            await reply_to_review(
                review_id=review.id,
                text=feedback_text,
                stars=review.stars,
                barcode=review.barcode,
                cabinet=cabinet,
                web_session=web_session
            )
        else:
            await redis_pipe.set(f'no-feedback:{client_id}:{review.barcode}', 'True', ex=12 * 60 * 60)

    else:
        feedback_text = await get_negative_feedback_text(client_id=client_id)

        if feedback_text is not None:
            await reply_to_review(
                review_id=review.id,
                text=feedback_text,
                stars=review.stars,
                barcode=review.barcode,
                cabinet=cabinet,
                web_session=web_session
            )

        if settings.complain:
            await complain_on_review(review_id=review.id, cabinet=cabinet)


async def reply_for_cabinet(
    client_id: str,
    cabinet_id: str,
    reviews: List[ReviewSchema],
    settings: SettingsSchema
) -> None:
    cabinet = CabinetSchema.get_by_id(id=cabinet_id)

    redis_client = get_redis_client_async()
    redis_pipe = redis_client.pipeline()

    async with aiohttp.ClientSession(raise_for_status=True) as web_session:
        tasks = [
            handle_review(
                client_id=client_id,
                review=review,
                cabinet=cabinet,
                settings=settings,
                web_session=web_session,
                redis_pipe=redis_pipe
            ) for review in reviews
        ]

        await gather(*tasks, return_exceptions=True)
        await redis_pipe.execute()


async def handler(event, context):
    for message in event['messages']:
        task_body = json.loads(message['details']['message']['body'])
        logger.info(f'Task body: {task_body}')

        client_id = task_body['clientId']
        cabinet_id = task_body['cabinetId']
        settings = await SettingsSchema.get_for_client_async(client_id=client_id)
        reviews = [
            ReviewSchema(
                id=review['id'],
                stars=review['stars'],
                barcode=review['barcode'],
                brand=review['brand']
            ) for review in task_body['reviews']
        ]

        await reply_for_cabinet(
            client_id=client_id,
            cabinet_id=cabinet_id,
            reviews=reviews,
            settings=settings
        )
        dispose_connections_async()
