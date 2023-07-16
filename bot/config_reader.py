from datetime import tzinfo
from functools import lru_cache

from pydantic import AnyUrl, BaseSettings, SecretStr
from pytz import timezone


class Settings(BaseSettings):
    TELEGRAM_TOKEN: SecretStr
    BASE_ENDPOINT: AnyUrl
    TIME_ZONE: str
    CONDITION_PERIOD_SEC: int

    @property
    def get_timezone(self) -> tzinfo:
        return timezone(self.TIME_ZONE)

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()


config = get_settings()
