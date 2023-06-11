from pydantic import BaseSettings

from app.settings.cloud import (RedisSettings, SecretSettings,
                                TelegramSettings, YCTriggerSettings,
                                YDBSettings, YMQSettings)
from app.settings.logic import LogicSettings
from app.settings.microsoft import MicrosoftSettings
from app.settings.yookassa import YooKassaSettings


class BackendSettings(BaseSettings):
    YDB: YDBSettings = YDBSettings()
    YMQ: YMQSettings = YMQSettings()
    TRIGGERS: YCTriggerSettings = YCTriggerSettings()
    SECRETS: SecretSettings = SecretSettings()
    REDIS: RedisSettings = RedisSettings()
    LOGIC: LogicSettings = LogicSettings()
    MICROSOFT: MicrosoftSettings = MicrosoftSettings()
    YOOKASSA: YooKassaSettings = YooKassaSettings()
    TELEGRAM: TelegramSettings = TelegramSettings()


_settings = BackendSettings()
