from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    BOT_TOKEN: str
    API_DEFAULT_URL: str
    SECRET_KEY: str


settings = Settings()
