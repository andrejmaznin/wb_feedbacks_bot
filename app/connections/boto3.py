import logging

import aioboto3
import boto3
import yandexcloud
from yandex.cloud.lockbox.v1.payload_service_pb2 import GetPayloadRequest
from yandex.cloud.lockbox.v1.payload_service_pb2_grpc import PayloadServiceStub

from app.settings import settings

logger = logging.getLogger(__name__)

boto_session = None
boto_session_async = None


def get_boto_session():
    global boto_session
    if boto_session is not None:
        return boto_session

    # initialize lockbox and read secret value
    yc_sdk = yandexcloud.SDK()
    channel = yc_sdk._channels.channel('lockbox-payload')
    lockbox = PayloadServiceStub(channel)
    response = lockbox.Get(GetPayloadRequest(secret_id=settings.SECRETS.main_id))

    # extract values from secret
    access_key = None
    secret_key = None
    for entry in response.entries:
        if entry.key == 'ACCESS_KEY_ID':
            access_key = entry.text_value
        elif entry.key == 'SECRET_ACCESS_KEY':
            secret_key = entry.text_value
    if access_key is None or secret_key is None:
        raise Exception('secrets required')

    logger.info('Key id: ' + access_key)

    # initialize boto session
    boto_session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    return boto_session


def get_boto_session_async():
    global boto_session_async
    if boto_session_async is not None:
        return boto_session_async

    # initialize lockbox and read secret value
    yc_sdk = yandexcloud.SDK()
    channel = yc_sdk._channels.channel('lockbox-payload')
    lockbox = PayloadServiceStub(channel)
    response = lockbox.Get(GetPayloadRequest(secret_id=settings.SECRETS.main_id))

    # extract values from secret
    access_key = None
    secret_key = None
    for entry in response.entries:
        if entry.key == 'ACCESS_KEY_ID':
            access_key = entry.text_value
        elif entry.key == 'SECRET_ACCESS_KEY':
            secret_key = entry.text_value
    if access_key is None or secret_key is None:
        raise Exception('secrets required')

    logger.info('Key id: ' + access_key)

    # initialize boto session
    boto_session_async = aioboto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    return boto_session_async
