from typing import Optional, Sequence

from ..repositories import TaskRepository
from ..models import Category, Task
from ..utils import *

class TaskService:

    def __init__(self, session):
        self.session = session
        self.task_repo = TaskRepository(session)

    # --------------- GET ----------------

    async def get_tasks(
            self,
            user_id: int,
            category_id: Optional[int] = None,
            tag_id: Optional[int] = None,
            status: Optional[str] = None,
            is_completed: Optional[bool] = None,
            from_date: Optional[str] = None,
            to_date: Optional[str] = None,
            search: Optional[str] = None
        ) -> Sequence[Task]:
        """
        Возвращает задачи пользователя с возможностью фильтрации.
        :param user_id: ID пользователя
        :param category_id: (опционально) ID категории
        :param tag_id: (опционально) ID тега
        :param status: (опционально) статус задачи
        :param from_date: (опционально) дата начала диапазона
        :param to_date: (опционально) дата конца диапазона
        :param is_completed: (опционально) флаг завершенности задачи
        :param search: (опционально) поисковый запрос по названию или описанию
        :return: список задач, соответствующих фильтрам
        """
        _positive_int_validator(user_id, "ID пользователя")
        if category_id is not None:
            _positive_int_validator(category_id, "ID категории")
        if tag_id is not None:
            _positive_int_validator(tag_id, "ID тега")
        if status is not None:
            _not_empty_str_validator(status, "статус задачи")
        if from_date is not None:
            _not_empty_str_validator(from_date, "дата начала диапазона")
        if to_date is not None:
            _not_empty_str_validator(to_date, "дата конца диапазона")
        if search is not None:
            _not_empty_str_validator(search, "поисковый запрос")

        return await self.task_repo.get_tasks(
            user_id=user_id,
            category_id=category_id,
            tag_id=tag_id,
            status=status,
            is_completed=is_completed,
            from_date=from_date,
            to_date=to_date,
            search=search
        )

    async def get_by_id(self, id: int) -> Optional[Task]:
        """
        Возвращает задачу по её ID.
        :param id: ID задачи
        :return: объект задачи или None, если задача не найдена
        """
        _positive_int_validator(id, "ID задачи")
        return await self.task_repo.get_by_id(id)

    # --------------- CREATE ----------------

    async def create(self, user_id: int, title: str, description: str, expiration_date: Optional[str],
                            is_completed: bool, category_id: int) -> Optional[Task]:
            """
            Создает новую задачу для пользователя.
            :param user_id: ID пользователя
            :param title: название задачи
            :param description: описание задачи
            :param expiration_date: дата истечения срока задачи в формате ISO
            :param is_completed: флаг завершенности задачи
            :param category_id: ID категории, к которой принадлежит задача
            :return: созданная задача или None, если создание не удалось
            """
            _positive_int_validator(user_id, "ID пользователя")
            _not_empty_str_validator(title, "название задачи")
            _not_empty_str_validator(description, "описание задачи")
            _positive_int_validator(category_id, "ID категории")
            return await self.task_repo.create(user_id, title, description, expiration_date, is_completed, category_id)

    # --------------- UPDATE ----------------

    async def patch(self, id: int, data: dict) -> Optional[Task]:
        """
        Обновляет данные задачи.
        :param id: ID задачи
        :param data: словарь с данными для обновления
        :return: обновленная задача или None, если задача не найдена
        """
        _positive_int_validator(id, "ID задачи")
        _not_empty_dict_validator(data, "данные для обновления задачи")
        _dict_keys_constant_validator(data, {"id", "user_id"})
        return await self.task_repo.patch(id, data)

    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        """
        Удаляет задачу по её ID.
        :param id: ID задачи
        :return: True, если задача была успешно удалена, иначе False
        """
        _positive_int_validator(id, "ID задачи")
        return await self.task_repo.delete(id)
