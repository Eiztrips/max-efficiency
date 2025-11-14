import requests
from typing import List, Dict, Any, Optional, Sequence

from ..settings import settings

API_DEFAULT_URL = settings.API_DEFAULT_URL

class CategoryService:

    @staticmethod
    def create(max_user_id: int, name: str, description: str = "") -> Dict[str, Any]:
        """
        Создать категорию для пользователя.
        :param max_user_id: ID пользователя
        :param name: Название категории
        :param description: Описание категории
        :return: Данные созданной категории в виде словаря
        """
        url = f"{API_DEFAULT_URL}/categories"
        category_data = {
            "max_user_id": max_user_id,
            "name": name,
            "description": description
        }
        response = requests.post(url, json=category_data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def delete(category_id: int) -> None:
        """
        Удалить категорию по ID.
        :param category_id: ID категории
        """
        url = f"{API_DEFAULT_URL}/categories/{category_id}"
        response = requests.delete(url)
        response.raise_for_status()

    @staticmethod
    def rename(category_id: int, new_name: str) -> Dict[str, Any]:
        """
        Переименовать категорию.
        :param category_id: ID категории
        :param new_name: Новое название категории
        :return: Данные обновленной категории в виде словаря
        """
        url = f"{API_DEFAULT_URL}/categories/{category_id}"
        update_data = {"name": new_name}
        response = requests.patch(url, json=update_data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def rename_description(category_id: int, new_description: str) -> Dict[str, Any]:
        """
        Обновить описание категории.
        :param category_id: ID категории
        :param new_description: Новое описание категории
        :return: Данные обновленной категории в виде словаря
        """
        url = f"{API_DEFAULT_URL}/categories/{category_id}"
        update_data = {"description": new_description}
        response = requests.patch(url, json=update_data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_joined_users(category_id: int) -> Sequence[Dict[str, Any]]:
        """
        Получить всех пользователей, связанных с категорией.
        :param category_id: ID категории
        :return: Список пользователей, связанных с категорией
        """
        url = f"{API_DEFAULT_URL}/categories/{category_id}/users"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_tags(category_id: int) -> Sequence[Dict[str, Any]]:
        """
        Получить все теги в категории.
        :param category_id: ID категории
        :return: Список тегов в категории
        """
        url = f"{API_DEFAULT_URL}/categories/{category_id}/tags"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_tasks(category_id: int) -> Sequence[Dict[str, Any]]:
        """
        Получить все задачи в категории.
        :param category_id: ID категории
        :return: Список задач в категории
        """
        url = f"{API_DEFAULT_URL}/categories/{category_id}/tasks"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_by_id(category_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить категорию по ID.
        :param category_id: ID категории
        :return: Данные категории в виде словаря или None, если категория не найдена
        """
        url = f"{API_DEFAULT_URL}/categories/{category_id}"
        response = requests.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()




category_service = CategoryService()