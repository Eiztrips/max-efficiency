import requests
from typing import List, Dict, Any, Optional, Sequence

from ..settings import settings

API_DEFAULT_URL = settings.API_DEFAULT_URL

class TagService:
    @staticmethod
    def fetch_tag_tasks(tag_id: int) -> Sequence[Dict[str, Any]]:
        """
        Получить все задачи по тегу.
        :param tag_id: ID тега
        :return: Список задач с указанным тегом
        """
        url = f"{API_DEFAULT_URL}/tags/{tag_id}/tasks"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_by_id(tag_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить тег по ID.
        :param tag_id: ID тега
        :return: Данные тега в виде словаря или None, если тег не найден
        """
        url = f"{API_DEFAULT_URL}/tags/{tag_id}"
        response = requests.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    @staticmethod
    def delete(tag_id: int) -> None:
        """
        Удалить тег по ID.
        :param tag_id: ID тега
        """
        url = f"{API_DEFAULT_URL}/tags/{tag_id}"
        response = requests.delete(url)
        response.raise_for_status()

tag_service = TagService()