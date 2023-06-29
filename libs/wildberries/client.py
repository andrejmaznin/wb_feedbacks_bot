import logging
from typing import List

import aiohttp
import requests

from libs.wildberries.consts import WB_FEEDBACKS_API_URL, WB_HEADERS
from libs.wildberries.exceptions import WBAuthException
from libs.wildberries.schemas import ReviewSchema

logger = logging.getLogger(__name__)


class WildberriesAPIClient:
    base_url: str = WB_FEEDBACKS_API_URL

    @staticmethod
    def get_headers(token: str):
        return {
            'Authorization': token,
            **WB_HEADERS
        }

    def get_unanswered_reviews(self, token: str) -> List[ReviewSchema]:
        response = requests.get(
            url=self.base_url,
            headers=self.get_headers(token=token),
            params={
                'take': 20,
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
                has_complaint=review['isCreationSupplierComplaint']
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
                json=request_body
        ) as response:
            if response.status in (401, 403):
                raise WBAuthException
            data = await response.json()

        if data['error'] is True:
            logger.error(f'Error while answering review: error: {data["errorText"]}, body: {request_body}')

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
                json=request_body
        ) as response:
            if response.status in (401, 403):
                raise WBAuthException
            data = await response.json()

        if data['error'] is True:
            logger.error(f'Error while complaining on review: error: {data["errorText"]}, body: {request_body}')
