from typing import Optional, Sequence

from fastapi import HTTPException

from ..repositories import CategoryRepository
from ..models import User, Tag, Category, Task
from ..schemas import CategoryCreate, CategoryUsersUpdateV2
from ..utils import *


class CategoryService:

    def __init__(self, session):
        self.session = session
        self.category_repo = CategoryRepository(session)
        self.user_repo = CategoryRepository(session)

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Category]:
        """
        Возвращает категорию по её ID.
        :param id: ID категории
        :return: объект категории или None, если категория не найдена
        """
        _positive_int_validator(id, "ID категории")
        return await self.category_repo.get_by_id(id)

    async def get_joined_users(self, category_id: int) -> Sequence[User]:
        """
        Возвращает всех пользователей, связанных с категорией по её ID.
        :param category_id: ID категории
        :return: список пользователей, связанных с категорией
        """
        _positive_int_validator(category_id, "ID категории")
        return await self.category_repo.get_joined_users(category_id)

    async def get_tags(self, category_id: int) -> Sequence[Tag]:
        """
        Возвращает все теги в категории по её ID.
        :param category_id: ID категории
        :return: список тегов в категории
        """
        _positive_int_validator(category_id, "ID категории")
        return await self.category_repo.get_tags(category_id)

    async def get_tasks(self, category_id: int) -> Sequence[Task]:
        """
        Возвращает все задачи в категории по её ID.
        :param category_id: ID категории
        :return: список задач в категории
        """
        _positive_int_validator(category_id, "ID категории")
        return await self.category_repo.get_tasks(category_id)

    get_id_by_name_and_owner = CategoryRepository.get_id_by_name_and_owner

    # --------------- CREATE ----------------

    async def create(self, payload: CategoryCreate) -> Optional[Category]:
        """
        Создает новую категорию для пользователя.
        :param payload: данные для создания категории (CategoryCreate)
        :return: созданная категория или None, если создание не удалось
        """
        return await self.category_repo.create(payload)

    # --------------- UPDATE ----------------

    async def add_user(self, payload: CategoryUsersUpdateV2) -> Category:
        """
        Добавляет пользователя в категорию.
        :param payload: данные для добавления пользователя в категорию (CategoryUsersUpdate)
        :return: True, если пользователь добавлен, False если уже был или ошибка
        """
        added = await self.category_repo.add_user(payload)
        if not added:
            raise HTTPException(status_code=400, detail="Не удалось добавить пользователя в категорию")
        category = await self.category_repo.get_by_id(payload.id)
        return category

    async def remove_user(self, payload: CategoryUsersUpdateV2) -> Category:
        """
        Удаляет пользователя из категории.
        :param payload: данные для удаления пользователя из категории (CategoryUsersUpdate)
        :return: True, если пользователь удален, False если не был в категории или ошибка
        """
        removed = await self.category_repo.remove_user(payload)
        if not removed:
            raise HTTPException(status_code=400, detail="Не удалось удалить пользователя из категории")
        category = await self.category_repo.get_by_id(payload.id)
        return category
    
    # --------------- DELETE ----------------

    async def delete(self, id: int) -> None:
        """
        Удаляет категорию по её ID.
        :param id: ID категории
        :return: True, если категория была успешно удалена, иначе False
        """
        _positive_int_validator(id, "ID категории")

        category = await self.category_repo.get_by_id(id)
        _category_exists_validator(category)

        deleted = await self.category_repo.delete(id)
        if not deleted:
            raise HTTPException(status_code=400, detail="Не удалось удалить категорию")