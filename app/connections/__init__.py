import telebot

from app.settings import settings

from .boto3 import get_boto_session
from .object_storage import get_storage_client
from .redis import get_redis_client, get_redis_client_async
from .ydb import (dispose_connections, get_driver, get_driver_async,
                  get_session_pool, get_session_pool_async)
from .ymq import (get_reply_queue, get_reply_queue_async, get_scan_queue,
                  get_scan_queue_async, get_update_queue,
                  get_update_queue_async)
from .yoo_kassa import config_yookassa

bot = telebot.TeleBot(token=settings.TELEGRAM.main_token)
