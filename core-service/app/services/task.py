import uuid
from fastapi import HTTPException
from typing import Optional, Sequence

from . import UserService
from .redis.redis import RedisTaskService
from ..repositories import TaskRepository, TagRepository, CategoryRepository
from ..models import Task
from ..schemas import TaskCreate, TaskQuery, TaskUpdate
from ..schemas.ai import InputMessage, APIInputRequest, TaskInputRequest, RedisTaskMessage
from .kafka import kafka_producer


class TaskService:

    def __init__(self, session):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.tag_repo = TagRepository(session)
        self.category_repo = CategoryRepository(session)
        self.user_service = UserService(session)


    # --------------- AI ----------------

    async def generate_task(self, payload: APIInputRequest) -> None:
        """
        Генерирует задачу на основе входного сообщения с использованием AI.
        :param payload: входное сообщение в формате InputMessage
        :return: сгенерированная задача
        """
        user_id = await self.user_service.map_max_user_id_to_user_id(payload.max_user_id)
        task_id = str(uuid.uuid4())
        all_tag_entities = await self.tag_repo.get_by_user_id(user_id)
        all_category_entities = await self.category_repo.get_by_user_id(user_id)

        message = InputMessage(
            task_id=task_id,
            prompt=payload.prompt,
            tags=[tag.name for tag in all_tag_entities],
            categories=[category.name for category in all_category_entities]
        )

        redis_data = RedisTaskMessage(
            task_id=task_id,
            user_id=user_id,
            category_id=payload.category_id
        )

        await RedisTaskService.save_task(task_id, redis_data)

        await kafka_producer.send_task_request(message)

    # --------------- GET ----------------

    async def get_tasks(self, payload: TaskQuery) -> Sequence[Task]:
        """
        Возвращает задачи пользователя с возможностью фильтрации.
        :param payload: данные для фильтрации задач в формате TaskQuery
        :return: список задач, соответствующих фильтрам
        """
        return await self.task_repo.get_tasks(payload)

    async def get_by_id(self, id: int) -> Optional[Task]:
        """
        Возвращает задачу по её ID.
        :param id: ID задачи
        :return: объект задачи или None, если задача не найдена
        """
        return await self.task_repo.get_by_id(id)

    # --------------- CREATE ----------------

    async def create(self, payload: TaskInputRequest) -> Optional[Task]:
            """
            Создает новую задачу для пользователя.
            :param payload: данные для создания задачи в формате TaskInputRequest
            :return: созданная задача или None, если создание не удалось
            """
            user_id = await self.user_service.map_max_user_id_to_user_id(payload.max_user_id)
            task_create = TaskCreate(
                user_id=user_id,
                title=payload.title,
                description=payload.description,
                category_id=payload.category_id,
                expiration_date=payload.expiration_date
            )
            return await self.task_repo.create(task_create)

    # --------------- UPDATE ----------------

    async def patch(self, payload: TaskUpdate) -> Optional[Task]:
        """
        Обновляет данные задачи.
        :param payload: данные для обновления задачи в формате TaskUpdate
        :return: обновленная задача или None, если задача не найдена
        """
        return await self.task_repo.patch(payload)

    # --------------- TAGS ----------------

    async def update_task_tags(self, task_id: int, tag_ids: list[int]) -> Optional[Task]:
        """
        Обновляет теги задачи (заменяет все теги)
        :param task_id: ID задачи
        :param tag_ids: список ID тегов
        :return: обновленная задача или None
        """
        return await self.task_repo.update_task_tags(task_id, tag_ids)

    # --------------- DELETE ----------------

    async def delete(self, id: int) -> None:
        """
        Удаляет задачу по её ID.
        :param id: ID задачи
        :return: True, если задача была успешно удалена, иначе False
        """
        deleted = await self.task_repo.delete(id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")
