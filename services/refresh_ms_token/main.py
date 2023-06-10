import json
import logging

from flask import request, Blueprint

from libs.microsoft import get_ms_auth_client
from libs.ydb.utils import prepare_and_execute_query

logger = logging.getLogger(__name__)

blueprint = Blueprint('microsoft', __name__)


def get_token(auth_code: str) -> None:
    ms_auth_client = get_ms_auth_client()

    access_token, refresh_token = ms_auth_client.get_tokens(auth_code=auth_code)
    prepare_and_execute_query(
        'DECLARE $credentialId AS String;'
        'DECLARE $accessToken AS String;'
        'DECLARE $refreshToken AS String;'
        'UPSERT INTO admin_credentials (id, ms_access_token, ms_refresh_token, created_at) '
        'VALUES ($credentialId, $accessToken, $refreshToken, CurrentUTCTimestamp())',
        credentialId='andrew',
        accessToken=access_token,
        refreshToken=refresh_token
    )


def refresh_ms_token() -> None:
    ms_auth_client = get_ms_auth_client()

    rows = prepare_and_execute_query(
        'DECLARE $credentialId AS String;'
        'SELECT ms_refresh_token FROM admin_credentials WHERE id=$credentialId',
        credentialId='andrew'
    )
    if not rows:
        return

    refresh_token = rows[0]['ms_refresh_token'].decode('utf-8')
    new_access_token, new_refresh_token = ms_auth_client.refresh_tokens(refresh_token=refresh_token)
    prepare_and_execute_query(
        'DECLARE $credentialId AS String;'
        'DECLARE $accessToken AS String;'
        'DECLARE $refreshToken AS String;'
        'UPSERT INTO admin_credentials (id, ms_access_token, ms_refresh_token, created_at) '
        'VALUES ($credentialId, $accessToken, $refreshToken, CurrentUTCTimestamp())',
        credentialId='andrew',
        accessToken=new_access_token,
        refreshToken=new_refresh_token
    )


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


@blueprint.route('/', methods=['GET', 'POST'])
def handle_refresh_request():
    refresh_ms_token()
    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }
