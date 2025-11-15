from aiokafka import AIOKafkaConsumer
import json
import asyncio
import random

from sqlalchemy.ext.asyncio import AsyncSession

from ..redis import RedisTaskService
from ...database import get_db
from ...models import Tag
from ...schemas import TaskCreate, TagCreate, TagUpdate
from ...config import settings
from app.schemas.ai import OutputMessage

# Палитра цветов для тегов
TAG_COLORS = [
    "#ef4444",  # red
    "#f97316",  # orange
    "#f59e0b",  # amber
    "#eab308",  # yellow
    "#84cc16",  # lime
    "#22c55e",  # green
    "#10b981",  # emerald
    "#14b8a6",  # teal
    "#06b6d4",  # cyan
    "#0ea5e9",  # sky
    "#3b82f6",  # blue
    "#6366f1",  # indigo
    "#8b5cf6",  # violet
    "#a855f7",  # purple
    "#d946ef",  # fuchsia
    "#ec4899",  # pink
    "#f43f5e",  # rose
]


def get_task_service(db: AsyncSession = get_db):
    from app.services import TaskService
    return TaskService(db)

def get_category_service(db: AsyncSession = get_db):
    from app.services import CategoryService
    return CategoryService(db)

def get_tag_service(db: AsyncSession = get_db):
    from app.services import TagService
    return TagService(db)

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
            from app.services import TaskService, CategoryService, TagService

            task_service = TaskService(session)
            tag_service = TagService(session)
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

            # Обработка тегов от нейросети
            if task_data.tags and len(task_data.tags) > 0:
                tag_ids = []
                for tag_name in task_data.tags:
                    # Получаем или создаем тег с рандомным цветом
                    random_color = random.choice(TAG_COLORS)
                    tag = await tag_service.get_or_create_by_name(
                        name=tag_name.strip(),
                        category_id=category_id,
                        color=random_color
                    )
                    if tag:
                        tag_ids.append(tag.id)
                
                # Привязываем теги к задаче
                if tag_ids:
                    await task_service.update_task_tags(created_task.id, tag_ids)
                    print(f"Добавлено {len(tag_ids)} тегов к задаче {created_task.id}")

            await session.commit()
            print(f"Получено сообщение: {message}")
        finally:
            await session.close()


kafka_consumer = KafkaConsumerService()
