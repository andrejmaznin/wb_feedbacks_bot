from pydantic import BaseSettings, Field


class LogicSettings(BaseSettings):
    price_1: int = Field(499, env='PRICE_1')
    price_3: int = Field(1249, env='PRICE_3')
    price_5: int = Field(2249, env='PRICE_5')
    scan_delay: int = Field(300, env='SCAN_DELAY')
    max_cabinets: int = Field(5, env='MAX_CABINETS')
