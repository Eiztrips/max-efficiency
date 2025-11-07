from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file="../.env", case_sensitive=True)

    BOT_TOKEN: str

settings = Settings()