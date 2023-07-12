import json
import logging

from flask import Blueprint, request

from libs.microsoft import get_ms_client
from libs.microsoft.auth import get_token

logger = logging.getLogger(__name__)

blueprint = Blueprint('microsoft', __name__)


@blueprint.get('/code')
def handle_auth_code():
    code = request.args.get('code')
    if code is None:
        return
    get_token(auth_code=code)

    ms_client = get_ms_client()
    print(f'Test item metadata: {ms_client.get_item(item_id="3A822AFD6B06B1F4!358")}')

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }


@blueprint.get('/admin/children')
def get_folder_children():
    ms_client = get_ms_client()

    return {
        'statusCode': 200,
        'contents': ms_client.get_children(path=request.args.get('path'))
    }
