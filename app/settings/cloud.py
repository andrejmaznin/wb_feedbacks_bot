from pydantic import BaseSettings, Field


class YDBSettings(BaseSettings):
    endpoint: str = Field(..., env='YDB_ENDPOINT')
    database: str = Field(..., env='YDB_DATABASE')


class YMQSettings(BaseSettings):
    scan_id: str = Field(..., env='SCAN_QUEUE_ID')
    scan_url: str = Field(..., env='SCAN_QUEUE_URL')
    reply_id: str = Field(..., env='REPLY_QUEUE_ID')
    reply_url: str = Field(..., env='REPLY_QUEUE_URL')
    update_id: str = Field(..., env='UPDATE_QUEUE_ID')
    update_url: str = Field(..., env='UPDATE_QUEUE_URL')


class YCTriggerSettings(BaseSettings):
    ms_refresh: str = Field(..., env='REFRESH_TRIGGER_ID')


class RedisSettings(BaseSettings):
    url: str = Field(..., env='REDIS_URL')


class TelegramSettings(BaseSettings):
    main_token: str = Field(..., env='TG_MAIN_TOKEN')


class SecretSettings(BaseSettings):
    main_id: str = Field(..., env='SECRET_ID')
