from aiokafka import AIOKafkaConsumer
import json
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from ..redis import RedisTaskService
from ...database import get_db
from ...schemas import TaskCreate
from ...config import settings
from app.schemas.ai import OutputMessage


def get_task_service(db: AsyncSession = get_db):
    from app.services import TaskService
    return TaskService(db)

def get_category_service(db: AsyncSession = get_db):
    from app.services import CategoryService
    return CategoryService(db)

class KafkaConsumerService:
    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_AI_RESPONSE_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        await self.consumer.start()
        self.running = True
        asyncio.create_task(self.consume())

    async def stop(self):
        self.running = False
        if self.consumer:
            await self.consumer.stop()

    async def consume(self):
        async for message in self.consumer:
            try:
                output_message = OutputMessage(**message.value)
                await self.process_message(output_message)
            except Exception as e:
                print(f"Ошибка при обработке сообщения: {e}")

    async def process_message(self, message: OutputMessage):
        db_gen = get_db()
        session = await db_gen.__anext__()

        try:
            from app.services import TaskService, CategoryService

            task_service = TaskService(session)
            redis_data = await RedisTaskService.get_task(task_id=message.task_id)
            task_data = message.task

            if redis_data.category_id:
                category_id = redis_data.category_id
            else:
                # пока модель может выдавать несуществующие категории, менять регистр и т. д.
                # в данный момент валидация в schemas.category APIInputRequest отлавливает пустые категории
                print(task_data.category, redis_data.user_id)
                category_service = CategoryService(session)
                category_id = await category_service.get_id_by_name_and_owner(
                    task_data.category,
                    redis_data.user_id
                )


            task = TaskCreate(
                user_id=redis_data.user_id,
                title=task_data.title,
                description=task_data.description,
                expiration_date=task_data.expiration_date,
                is_completed=False,
                category_id=category_id
            )

            created_task = await task_service.create(task)
            if not created_task:
                # В бота блин надо будет ошибку слать
                print(f"Ошибка при создании задачи для task_id: {message.task_id}")
                return

            await session.commit()
            print(f"Получено сообщение: {message}")
        finally:
            await session.close()


kafka_consumer = KafkaConsumerService()
