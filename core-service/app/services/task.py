from fastapi import HTTPException
from typing import Optional, Sequence

from ..repositories import TaskRepository
from ..models import Task
from ..schemas import TaskCreate, TaskQuery, TaskUpdate

class TaskService:

    def __init__(self, session):
        self.session = session
        self.task_repo = TaskRepository(session)

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

    async def create(self, payload: TaskCreate) -> Optional[Task]:
            """
            Создает новую задачу для пользователя.
            :param payload: данные для создания задачи в формате TaskCreate
            :return: созданная задача или None, если создание не удалось
            """
            return await self.task_repo.create(payload)

    # --------------- UPDATE ----------------

    async def patch(self, payload: TaskUpdate) -> Optional[Task]:
        """
        Обновляет данные задачи.
        :param payload: данные для обновления задачи в формате TaskUpdate
        :return: обновленная задача или None, если задача не найдена
        """
        return await self.task_repo.patch(payload)

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
