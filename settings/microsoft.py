from pydantic import BaseSettings, Field


class MicrosoftSettings(BaseSettings):
    client_id: str = Field(..., env='MS_CLIENT_ID')
    client_secret: str = Field(..., env='MS_CLIENT_SECRET')
    redirect_url: str = Field(..., env='MS_REDIRECT_URL')


settings = MicrosoftSettings()
