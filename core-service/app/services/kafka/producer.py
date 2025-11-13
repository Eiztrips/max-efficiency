from aiokafka import AIOKafkaProducer
import json
from ...config import settings
from app.schemas.ai import InputMessage


class KafkaProducerService:
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send_task_request(self, message: InputMessage):
        if not self.producer:
            raise RuntimeError("Кафка продюсер не инициализирован.")

        await self.producer.send(
            settings.KAFKA_AI_REQUEST_TOPIC,
            value=message.model_dump()
        )

kafka_producer = KafkaProducerService()
