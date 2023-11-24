import logging
from typing import List

import aiohttp
import requests

from libs.wildberries.consts import WB_FEEDBACKS_API_URL, WB_HEADERS
from libs.wildberries.exceptions import WBAuthException, WBCreateComplaintException
from libs.wildberries.schemas import ReviewSchema

logger = logging.getLogger(__name__)


class WildberriesAPIClient:
    base_url: str = WB_FEEDBACKS_API_URL

    @staticmethod
    def get_headers(token: str):
        return {
            'Authorization': token
        }

    def get_unanswered_reviews(self, token: str) -> List[ReviewSchema]:
        response = requests.get(
            url=self.base_url,
            headers=self.get_headers(token=token),
            params={
                'take': 100,
                'skip': 0,
                'hasSupplierComplaint': False,
                'isAnswered': False,
                'order': 'dateDesc'
            }
        )

        if response.status_code in (401, 403):
            logger.error(response.text)
            raise WBAuthException

        reviews = response.json()['data']['feedbacks']
        return [
            ReviewSchema(
                id=review['id'],
                stars=review['productValuation'],
                barcode=str(review['productDetails']['nmId']),
                brand=review['productDetails']['brandName'],
            ) for review in reviews
        ]

    async def reply_to_review_async(
        self,
        review_id: str,
        text: str,
        token: str,
        web_session: aiohttp.ClientSession
    ) -> None:
        request_body = {'id': review_id, 'text': text}
        async with web_session.patch(
            url=self.base_url,
            headers=self.get_headers(token=token),
            json=request_body,
            timeout=2
        ) as response:
            if response.status in (401, 403):
                raise WBAuthException
            data = await response.json()

        if data['error'] is True:
            print(f'Error while answering review: error: {data["errorText"]}, body: {request_body}')

    async def complain_on_review_async(
        self,
        review_id: str,
        token: str,
        web_session: aiohttp.ClientSession
    ) -> None:
        request_body = {'id': review_id, 'createSupplierComplaint': True}
        async with web_session.patch(
            url=self.base_url,
            headers=self.get_headers(token=token),
            json=request_body,
            timeout=2
        ) as response:
            if response.status in (401, 403):
                raise WBAuthException
            data = await response.json()

        if data['error'] is True:
            if 'Создание жалобы на отзыв недоступно' in data['errorText']:
                raise WBCreateComplaintException
        print(f'Error while complaining on review: error: {data["errorText"]}, body: {request_body}')
