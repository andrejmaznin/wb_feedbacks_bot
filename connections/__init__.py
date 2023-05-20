import os

import telebot
import yadisk

from .boto3 import get_boto_session
from .object_storage import get_storage_client
from .ydb import get_driver
from .ydb import get_driver_async
from .ydb import get_session_pool
from .ydb import get_session_pool_async
from .ymq import get_cabinets_queue_async, get_reviews_queue, get_reviews_queue_async
from .yoo_kassa import config_yookassa

bot = telebot.TeleBot(os.getenv('TG_BOT_TOKEN'))
disk_client = yadisk.YaDisk(token=os.getenv('YADISK_TOKEN'))
