from typing import Optional, Sequence

from ..repositories import TagRepository
from ..models import Tag, Category, Task

class TagService:

    def __init__(self, session):
        self.session = session
        self.tag_repo = TagRepository(session)

    # --------------- GET ----------------

    async def get_all_tasks_by_tag_id(self, tag_id: int) -> Sequence[Task]:
        """
        Возвращает все задачи, связанные с тегом по его ID.
        :param tag_id: ID тега
        :return: список задач, связанных с тегом
        """
        _positive_int_validator(tag_id, "ID тега")
        return await self.tag_repo.get_all_tasks_by_tag_id(tag_id)

    # --------------- CREATE ----------------

    async def create_tag(self, category_id: int, name: str, color: str = "#FFFFFF") -> Optional[Tag]:
        """
        Создает новый тег в категории.
        :param category_id: ID категории, к которой принадлежит тег
        :param name: название тега
        :param color: цвет тега в формате HEX
        :return: созданный тег или None, если создание не удалось
        """
        _positive_int_validator(category_id, "ID категории")
        _not_empty_str_validator(name, "название тега")
        async with self.session.begin():
            return await self.tag_repo.create(category_id, name, color)

    # --------------- UPDATE ----------------

    async def patch_tag(self, id: int, data: dict) -> Optional[Tag]:
        """
        Обновляет данные тега.
        :param id: ID тега
        :param data: словарь с данными для обновления
        :return: обновленный объект тега или None, если тег не найден
        """
        _positive_int_validator(id, "ID тега")
        _not_empty_dict_validator(data, "данные для обновления тега")
        _dict_keys_constant_validator(data, {"id", "category_id"})
        async with self.session.begin():
            return await self.tag_repo.patch(id, data)

    # --------------- DELETE ----------------

    async def delete_tag(self, id: int) -> bool:
        """
        Удаляет тег по его ID.
        :param id: ID тега
        :return: True, если тег был успешно удален, иначе False
        """
        _positive_int_validator(id, "ID тега")
        async with self.session.begin():
            return await self.tag_repo.delete(id)


# ну или хотя бы вынести в отдельный класс...
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
