from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DATABASE_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_AI_REQUEST_TOPIC: str
    KAFKA_AI_RESPONSE_TOPIC: str
    KAFKA_CONSUMER_GROUP: str

    REDIS_URL: str
    REDIS_CACHE_TTL: int

    #SECRET_KEY: str

settings = Settings()
