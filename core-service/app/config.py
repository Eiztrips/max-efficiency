from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    DATABASE_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_ROUTE_TOPIC: str
    KAFKA_AI_RESPONSE_TOPIC: str

    SECRET_KEY: str

settings = Settings()
