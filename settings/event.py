from pydantic import BaseSettings, Field


class EventIDSettings(BaseSettings):
    scan_cabinet: str = Field(..., env='SCAN_QUEUE_ID')
    reply_cabinet: str = Field(..., env='REPLY_QUEUE_ID')
    ms_refresh: str = Field(..., env='REFRESH_TRIGGER_ID')
    update_feedbacks: str = Field(..., env='UPDATE_QUEUE_ID')


settings = EventIDSettings()
