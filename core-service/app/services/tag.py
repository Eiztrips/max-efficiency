from typing import Optional, Sequence

from ..repositories import TagRepository
from ..models import Tag, Task
from ..schemas import TagCreate, TagUpdate
from ..utils import *

class TagService:

    def __init__(self, session):
        self.session = session
        self.tag_repo = TagRepository(session)

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Tag]:
        """
        Возвращает тег по его ID.
        :param id: ID тега
        :return: объект тега или None, если тег не найден
        """
        return await self.tag_repo.get_by_id(id)

    async def get_tasks(self, tag_id: int) -> Sequence[Task]:
        """
        Возвращает все задачи, связанные с тегом по его ID.
        :param tag_id: ID тега
        :return: список задач, связанных с тегом
        """
        return await self.tag_repo.get_tasks(tag_id)

    # --------------- CREATE ----------------

    async def create(self, payload: TagCreate) -> Optional[Tag]:
        """
        Создает новый тег в категории.
        :param payload: данные для создания тега (TagCreate)
        :return: созданный тег или None, если создание не удалось
        """
        return await self.tag_repo.create(payload)

    async def get_or_create_by_name(self, name: str, category_id: int, color: str = "#3b82f6") -> Optional[Tag]:
        """
        Получает существующий тег или создает новый, если тег с таким именем не существует в категории.
        :param name: название тега
        :param category_id: ID категории
        :param color: цвет тега (по умолчанию синий)
        :return: объект тега
        """
        # Проверяем, существует ли тег с таким именем в категории
        existing_tag = await self.tag_repo.get_by_name_and_category(name, category_id)
        if existing_tag:
            return existing_tag
        
        # Создаем новый тег
        tag_create = TagCreate(
            name=name,
            category_id=category_id,
            color=color
        )
        return await self.tag_repo.create(tag_create)

    # --------------- UPDATE ----------------

    async def patch(self, payload: TagUpdate) -> Optional[Tag]:
        """
        Обновляет данные тега.
        :param payload: данные для обновления тега (TagUpdate)
        :return: обновленный объект тега или None, если тег не найден
        """
        return await self.tag_repo.patch(payload)

    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        """
        Удаляет тег по его ID.
        :param id: ID тега
        :return: True, если тег был успешно удален, иначе False
        """
        return await self.tag_repo.delete(id)

