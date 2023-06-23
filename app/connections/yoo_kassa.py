from yookassa import Configuration

from app.settings import settings


def config_yookassa():
    Configuration.account_id = settings.YOOKASSA.account_id
    Configuration.secret_key = settings.YOOKASSA.secret_key
