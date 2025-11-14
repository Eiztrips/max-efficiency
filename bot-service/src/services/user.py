import requests
from typing import List, Dict, Any, Optional, Sequence

from ..settings import settings

API_DEFAULT_URL = settings.API_DEFAULT_URL

class UserService:

    @staticmethod
    def get_user_by_max_user_id(max_user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить пользователя по max_user_id.
        :param max_user_id: ID пользователя
        :return: Данные пользователя в виде словаря или None, если пользователь не найден
        """
        url = f"{API_DEFAULT_URL}/users/{max_user_id}"
        response = requests.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    @staticmethod
    def create_user(max_user_id: int, username: str) -> Dict[str, Any]:
        """
        Cоздать пользователя.
        :param max_user_id: ID пользователя
        :param username: Имя пользователя
        :return: Данные пользователя в виде словаря
        """
        url = f"{API_DEFAULT_URL}/users/{max_user_id}"
        response = requests.get(url)
        if response.status_code == 404:
            user_create = {"max_user_id": max_user_id, "username": username}
            create_response = requests.post(f"{API_DEFAULT_URL}/users", json=user_create)
            create_response.raise_for_status()
            return create_response.json()
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_user_categories(max_user_id) -> Sequence[Dict[str, Any]]:
        """
        Получить все категории пользователя.
        :param max_user_id: ID пользователя
        :return: Список категорий пользователя
        """
        url = f"{API_DEFAULT_URL}/users/{max_user_id}/categories"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_user_tasks(max_user_id) -> Sequence[Dict[str, Any]]:
        """
        Получить все задачи пользователя.
        :param max_user_id: ID пользователя
        :return: Список задач пользователя
        """
        url = f"{API_DEFAULT_URL}/users/{max_user_id}/tasks"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_user_tags(max_user_id) -> Sequence[Dict[str, Any]]:
        """
        Получить все теги пользователя.
        :param max_user_id: ID пользователя
        :return: Список тегов пользователя
        """
        url = f"{API_DEFAULT_URL}/users/{max_user_id}/tags"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

user_service = UserService()