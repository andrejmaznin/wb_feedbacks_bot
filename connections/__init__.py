import os

import telebot
import yadisk

from .boto3 import get_boto_session
from .database import get_driver
from .database import get_session_pool
from .object_storage import get_storage_client

bot = telebot.TeleBot(os.getenv('TG_BOT_TOKEN'))
disk_client = yadisk.YaDisk(token=os.getenv('YADISK_TOKEN'))
