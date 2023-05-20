import os

from yookassa import Configuration


def config_yookassa():
    Configuration.account_id = os.getenv('YOOKASSA_ACCOUNT_ID')
    Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')
