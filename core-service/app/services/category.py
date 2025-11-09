from typing import Optional, Sequence

from ..repositories import CategoryRepository
from ..models import User, Tag, Category, Task
from ..schemas import CategoryUpdate


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

    async def get_users_by_category_id(self, category_id: int) -> Sequence[User]:
        """
        Возвращает всех пользователей, связанных с категорией по её ID.
        :param category_id: ID категории
        :return: список пользователей, связанных с категорией
        """
        _positive_int_validator(category_id, "ID категории")
        return await self.category_repo.get_all_joined_users_in_category(category_id)

    async def get_tags_by_category_id(self, category_id: int) -> Sequence[Tag]:
        """
        Возвращает все теги в категории по её ID.
        :param category_id: ID категории
        :return: список тегов в категории
        """
        _positive_int_validator(category_id, "ID категории")
        return await self.category_repo.get_all_tags_in_category(category_id)

    async def get_tasks_by_category_id(self, category_id: int) -> Sequence[Task]:
        """
        Возвращает все задачи в категории по её ID.
        :param category_id: ID категории
        :return: список задач в категории
        """
        _positive_int_validator(category_id, "ID категории")
        return await self.category_repo.get_all_tasks_in_category(category_id)

    # --------------- CREATE ----------------

    async def create(self, user_id: int, name: str, description: str = "") -> Optional[Category]:
        """
        Создает новую категорию для пользователя.
        :param user_id: ID пользователя, которому принадлежит категория
        :param name: название категории
        :param description: описание категории
        :return: созданная категория или None, если создание не удалось
        """
        _positive_int_validator(user_id, "ID пользователя")
        _not_empty_str_validator(name, "название категории")
        return await self.category_repo.create(user_id, name, description)


    # --------------- UPDATE ----------------

    async def add_user(self, category_id: int, user_id: int) -> Optional[CategoryUpdate]:
        """
        Добавляет пользователя в категорию.
        :param category_id: ID категории
        :param user_id: ID пользователя
        :return: True, если пользователь добавлен, False если уже был или ошибка
        """
        _positive_int_validator(category_id, "ID категории")
        _positive_int_validator(user_id, "ID пользователя")

        category = await self.category_repo.get_by_id(category_id)
        _category_exists_validator(category)
        if not await self.user_repo.get_by_id(user_id): raise ValueError("Пользователь не найден")
        return CategoryUpdate(success = await self.category_repo.add_user(category_id, user_id))
    
    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        """
        Удаляет категорию по её ID.
        :param id: ID категории
        :return: True, если категория была успешно удалена, иначе False
        """
        _positive_int_validator(id, "ID категории")

        category = await self.category_repo.get_by_id(id)
        _category_exists_validator(category)

        return await self.category_repo.delete(id)

# Что бы не оверинженерить оставлю так. При усложнении логики - перейти на пудантек в schemas
def _positive_int_validator(value: int, field_name: str):
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} должен быть положительным целым числом.")

def _not_empty_str_validator(value: str, field_name: str):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} должен быть непустой строкой.")

def _not_empty_dict_validator(value: dict, field_name: str):
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field_name} должен быть непустым словарем.")

def _dict_keys_constant_validator(data: dict, constant_keys: set[str]):
    for key in constant_keys:
        if key in data:
            raise ValueError(f"Нельзя изменять поле: {key}")

def _category_exists_validator(category: Category):
    if not category:
        raise ValueError("Категория не найдена")
