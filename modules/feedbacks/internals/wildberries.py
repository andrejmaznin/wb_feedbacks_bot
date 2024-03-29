import json
from asyncio import gather
from random import choice
from typing import List, Optional

import aiohttp
from redis.asyncio.client import Pipeline

from app.connections import get_redis_client, get_redis_client_async
from libs.wildberries import WildberriesAPIClient, get_wb_client
from libs.wildberries.exceptions import WBAuthException, WBCreateComplaintException
from libs.wildberries.schemas import ReviewSchema
from libs.ydb.utils import prepare_and_execute_query_async
from modules.cabinets import CabinetSchema
from modules.feedbacks.schemas import ReplySettingsSchema


def scan_cabinet(cabinet: CabinetSchema, client_id: str) -> List[ReviewSchema]:
    redis_client = get_redis_client()
    wb_client = get_wb_client()

    reviews = wb_client.get_unanswered_reviews(token=cabinet.token)
    no_feedback_keys = redis_client.mget(
        keys=[
            f'no-feedback:{cabinet.id}:{review.barcode}'
            for review in reviews
        ]
    )
    complained_keys = redis_client.mget(
        keys=[
            f'complained:{review.id}'
            for review in reviews
        ]
    )
    print('Reviews from WB:', len(reviews))
    reviews_to_reply = []
    for no_feedback, complained, review in zip(no_feedback_keys, complained_keys, reviews):
        if no_feedback is None:
            if 1 <= review.stars <= 3:
                if complained is None:
                    reviews_to_reply.append(review)
            else:
                reviews_to_reply.append(review)
    print('Reviews to reply:', len(reviews_to_reply))
    return reviews_to_reply


async def get_positive_feedback_text(cabinet_id: str, review: ReviewSchema) -> Optional[str]:
    rows = await prepare_and_execute_query_async(
        'DECLARE $cabinetId AS String;'
        'DECLARE $barcode AS String;'
        'SELECT pos_feedback FROM barcode_feedbacks '
        'WHERE cabinet_id=$cabinetId AND barcode=$barcode;',
        cabinetId=cabinet_id,
        barcode=review.barcode
    )
    if rows:
        return rows[0].pos_feedback.decode('utf-8')

    rows = await prepare_and_execute_query_async(
        'DECLARE $cabinetId AS String;'
        'DECLARE $brand AS String;'
        'SELECT pos_feedbacks FROM brand_feedbacks WHERE brand=$brand AND cabinet_id=$cabinetId',
        cabinetId=cabinet_id,
        brand=review.brand
    )
    if rows:
        feedbacks = json.loads(rows[0].pos_feedbacks)
        feedback = choice(feedbacks)
        return feedback.decode('utf-8') if isinstance(feedback, bytes) else feedback

    return None


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


async def handle_review(
    client_id: str,
    review: ReviewSchema,
    cabinet: CabinetSchema,
    settings: ReplySettingsSchema,
    web_session: aiohttp.ClientSession,
    redis_pipe: Pipeline,
    wb_client: WildberriesAPIClient
) -> None:
    if review.stars in [0, 4, 5]:
        feedback_text = await get_positive_feedback_text(cabinet_id=cabinet.id, review=review)
        if feedback_text is not None:
            try:
                await wb_client.reply_to_review_async(
                    review_id=review.id,
                    text=feedback_text,
                    token=cabinet.token,
                    web_session=web_session
                )
            except WBAuthException:
                print('Error while replying to review')
        else:
            await redis_pipe.set(f'no-feedback:{cabinet.id}:{review.barcode}', 'True', ex=2 * 60 * 60)
    else:
        pass
        ''''
        if settings.complain:
            try:
                await wb_client.complain_on_review_async(
                    review_id=review.id,
                    token=cabinet.token,
                    web_session=web_session
                )
                await redis_pipe.set(f'complained:{review.id}', 'True', ex=2 * 24 * 60 * 60)

            except WBCreateComplaintException:
                await redis_pipe.set(f'complained:{review.id}', 'True', ex=2 * 24 * 60 * 60)
        '''


async def reply_for_cabinet(
    client_id: str,
    cabinet_id: str,
    reviews: List[ReviewSchema],
    settings: ReplySettingsSchema
) -> None:
    cabinet = await CabinetSchema.get_by_id_async(id=cabinet_id)

    wb_client = get_wb_client()
    redis_client = get_redis_client_async()
    redis_pipe = redis_client.pipeline()

    async with aiohttp.ClientSession(raise_for_status=False) as web_session:
        tasks = [
            handle_review(
                client_id=client_id,
                review=review,
                cabinet=cabinet,
                settings=settings,
                web_session=web_session,
                redis_pipe=redis_pipe,
                wb_client=wb_client
            ) for review in reviews
        ]

        await gather(*tasks, return_exceptions=True)
        await redis_pipe.execute()
