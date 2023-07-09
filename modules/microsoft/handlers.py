import json
import logging
from typing import Dict

from flask import Blueprint, request

from libs.microsoft import get_ms_client
from modules.microsoft.internals import get_token, refresh_ms_token

logger = logging.getLogger(__name__)

blueprint = Blueprint('microsoft', __name__)


@blueprint.get('/code')
def handle_auth_code():
    code = request.args.get('code')
    if code is None:
        return
    get_token(auth_code=code)

    # ms_client = get_ms_client()
    # print(f'Test item metadata: {ms_client.get_item(item_id="3A822AFD6B06B1F4!358")}')

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


@blueprint.get('/refresh')
def refresh_request_handler():
    ms_client = get_ms_client()
    print(f'Test item metadata: {ms_client.get_item(item_id="3A822AFD6B06B1F4!358")}')

    refresh_ms_token()

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


def refresh_ms_token_handler(message: Dict) -> None:
    ms_client = get_ms_client()
    print(f'Test item metadata: {ms_client.get_item(item_id="3A822AFD6B06B1F4!358")}')

    refresh_ms_token()
