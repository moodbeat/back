from pydantic import AnyUrl, BaseSettings, SecretStr


class Settings(BaseSettings):
    telegram_token: SecretStr
    base_endpoint: AnyUrl

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
