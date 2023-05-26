import json

import requests
from flask import request, Blueprint

from libs.ydb.utils import prepare_and_execute_query
from services.refresh_ms_token.settings import settings as microsoft_settings

blueprint = Blueprint('microsoft', __name__)


def get_token(code: str) -> None:
    form_data = {
        'code': code,
        'client_id': microsoft_settings.client_id,
        'client_secret': microsoft_settings.client_secret,
        'scope': 'offline_access files.readwrite.all',
        'grant_type': 'authorization_code'
    }
    params = {'redirect_url': microsoft_settings.redirect_url}

    response = requests.post(
        url='https://login.microsoftonline.com/consumers/oauth2/v2.0/token',
        data=form_data,
        params=params
    )
    if response.status_code != 200:
        return

    data = response.json()
    access_token = data['access_token']
    refresh_token = data['refresh_token']

    prepare_and_execute_query(
        'DECLARE $credentialId AS String;'
        'DECLARE $accessToken AS String;'
        'DECLARE $refreshToken AS String;'
        'UPSERT INTO admin_credentials (id, ms_access_token, ms_refresh_token) '
        'VALUES ($credentialId, $accessToken, $refreshToken)',
        credentialId='andrew',
        accessToken=access_token,
        refreshToken=refresh_token
    )


def refresh_ms_token():
    rows = prepare_and_execute_query(
        'DECLARE $credentialId AS String;'
        'SELECT refresh_token FROM admin_credentials WHERE id=$credentialId',
        credentialId='andrew'
    )
    if not rows:
        return

    refresh_token = rows[0]['refresh_token'].decode('utf-8')

    form_data = {
        'refresh_token': refresh_token,
        'client_id': microsoft_settings.client_id,
        'client_secret': microsoft_settings.client_secret,
        'scope': 'offline_access files.readwrite.all',
        'grant_type': 'refresh_token'
    }
    response = requests.post(
        url='https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize',
        data=form_data
    )
    if response.status_code != 200:
        return

    data = response.json()
    new_access_token = data['access_token']
    new_refresh_token = data['refresh_token']

    prepare_and_execute_query(
        'DECLARE $credentialId AS String;'
        'DECLARE $accessToken AS String;'
        'DECLARE $refreshToken AS String;'
        'UPSERT INTO admin_credentials (id, ms_access_token, ms_refresh_token) '
        'VALUES ($credentialId, $accessToken, $refreshToken)',
        credentialId='andrew',
        accessToken=new_access_token,
        refreshToken=new_refresh_token
    )


@blueprint.get('/code')
def handle_auth_code():
    code = request.args.get('code')
    if code is None:
        return
    get_token(code=code)

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
