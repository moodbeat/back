import uuid
from datetime import tzinfo
from functools import lru_cache
from urllib.parse import urljoin

from pydantic import BaseSettings, HttpUrl, SecretStr
from pytz import timezone


class Settings(BaseSettings):
    TELEGRAM_TOKEN: SecretStr
    BASE_ENDPOINT: HttpUrl
    SELF_HOST: HttpUrl
    TIME_ZONE: str
    CONDITION_PERIOD_SEC: int
    WEB_HOOK_MODE: bool
    WEB_HOOK_HOST: HttpUrl
    WEB_APP_PORT: int
    REDIS_HOST: str
    REDIS_PORT: int
    SECRET_TOKEN: SecretStr = str(uuid.uuid4())

    @property
    def get_web_hook_url(self) -> str:
        return urljoin(self.WEB_HOOK_HOST, 'telegram_webhook/')

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
