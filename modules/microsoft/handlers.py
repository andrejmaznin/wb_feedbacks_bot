import json
from typing import Dict

from flask import Blueprint, request

from modules.microsoft.internals import get_token, refresh_ms_token

blueprint = Blueprint('microsoft', __name__)


@blueprint.get('/code')
def handle_auth_code():
    code = request.args.get('code')
    if code is None:
        return
    get_token(auth_code=code)

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


@blueprint.get('/refresh')
def refresh_request_handler():
    refresh_ms_token()

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


def refresh_ms_token_handler(message: Dict) -> None:
    refresh_ms_token()
