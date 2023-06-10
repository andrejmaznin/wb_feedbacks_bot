from yookassa import Configuration

from settings import yookassa_settings


def config_yookassa():
    Configuration.account_id = yookassa_settings.account_id
    Configuration.secret_key = yookassa_settings.secret_key
