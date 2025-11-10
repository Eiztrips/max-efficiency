from typing import Optional, Sequence

from ..repositories.user import UserRepository
from ..models import User, Tag, Category, Task

class UserService:

    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)

    # --------------- MAPPING ----------------

    async def map_max_user_id_to_user_id(self, max_user_id: int) -> Optional[int]:
        """
        Возвращает внутренний user_id по max_user_id.
        :param max_user_id: max_user_id пользователя
        :return: внутренний user_id или None, если пользователь не найден
        """
        _positive_int_validator(max_user_id, "max_user_id пользователя")
        return await self.user_repo.get_id_by_max_user_id(max_user_id)

    # --------------- GET USER ----------------

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Возвращает пользователя по его user_id.
        :param user_id: id пользователя
        :return: объект пользователя или None, если пользователь не найден
        """
        _positive_int_validator(user_id, "user_id пользователя")
        return await self.user_repo.get_by_id(user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Возвращает пользователя по его username.
        :param username: имя пользователя
        :return: объект пользователя или None, если пользователь не найден
        """
        _not_empty_str_validator(username, "username пользователя")
        return await self.user_repo.get_by_username(username)

    # --------------- GET USER RELATED DATA ----------------

    # возможно не пригодится
    async def get_tags(self, user_id: int) -> Sequence[Tag]:
        """
        Возвращает все теги пользователя по его user_id.
        :param user_id: id пользователя
        :return: список тегов пользователя
        """
        _positive_int_validator(user_id, "user_id пользователя")
        return await self.user_repo.get_tags_by_user_id(user_id)

    async def get_categories(self, user_id: int) -> Sequence[Category]:
        """
        Возвращает все категории пользователя по его user_id.
        :param user_id: id пользователя
        :return: список категорий пользователя
        """
        _positive_int_validator(user_id, "user_id пользователя")
        return await self.user_repo.get_categories_by_user_id(user_id)

    async def get_tasks(self, user_id: int) -> Sequence[Task]:
        """
        Возвращает все задачи пользователя по его user_id.
        :param user_id: id пользователя
        :return: список задач пользователя
        """
        _positive_int_validator(user_id, "user_id пользователя")
        return await self.user_repo.get_tasks_by_user_id(user_id)

    # --------------- CREATE USER ----------------

    async def get_or_create_user(self, max_user_id: int, username: str) -> User:
        """
        Создает нового пользователя.
        :param max_user_id: max_user_id пользователя
        :param username: имя пользователя
        :return: созданный объект пользователя
        """
        _positive_int_validator(max_user_id, "max_user_id пользователя")
        _not_empty_str_validator(username, "username пользователя")
        user_id = await self.user_repo.get_id_by_max_user_id(max_user_id)
        existing_user_by_max_user_id = await self.user_repo.get_by_id(user_id)
        return existing_user_by_max_user_id or await self.user_repo.create(max_user_id, username)

    # --------------- UPDATE USER ----------------

    async def patch(self, user_id: int, data: dict) -> Optional[User]:
        """
        Обновляет данные пользователя.
        :param user_id: user_id пользователя
        :param data: словарь с данными для обновления
        :return: обновленный объект пользователя или None, если пользователь не найден
        """
        _positive_int_validator(user_id, "ID пользователя")
        _not_empty_dict_validator(data, "данные для обновления пользователя")
        _dict_keys_constant_validator(data, {"id", "max_user_id"})
        return await self.user_repo.patch(user_id, data)

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
