import logging
import os

import yadisk

from connections.boto3 import get_boto_session

logger = logging.getLogger()

storage_client = None

disk_client = yadisk.YaDisk(token=os.getenv('YADISK_TOKEN'))


def get_storage_client():
    global storage_client
    if storage_client is not None:
        return storage_client

    storage_client = get_boto_session().client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        region_name='ru-central1'
    )
    return storage_client
