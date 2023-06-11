from pydantic import BaseSettings, Field


class LogicSettings(BaseSettings):
    subscription_price: int = Field(2990, env='SUBSCRIPTION_PRICE')
    scan_delay: int = Field(300, env='SCAN_DELAY')
    max_cabinets: int = Field(5, env='MAX_CABINETS')
