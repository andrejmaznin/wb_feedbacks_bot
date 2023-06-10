from pydantic import BaseSettings, Field


class YooKassaSettings(BaseSettings):
    account_id: str = Field(..., env='YOOKASSA_ACCOUNT_ID')
    secret_key: str = Field(..., env='YOOKASSA_SECRET_KEY')


settings = YooKassaSettings()
