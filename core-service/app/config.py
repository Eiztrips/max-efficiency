from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    DATABASE_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_AI_REQUEST_TOPIC: str
    KAFKA_AI_RESPONSE_TOPIC: str
    KAFKA_CONSUMER_GROUP: str

    REDIS_URL: str
    REDIS_CACHE_TTL: int

    #SECRET_KEY: str

settings = Settings()
