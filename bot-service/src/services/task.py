import requests
from typing import List, Dict, Any, Optional, Sequence

from ..settings import settings

API_DEFAULT_URL = settings.API_DEFAULT_URL

class TaskService:
    """
    class TaskQuery(BaseModel):
    user_id: int
    category_id: Optional[int] = None
    tag_id: Optional[int] = None
    status: Optional[str] = None
    is_completed: Optional[bool] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    search: Optional[str] = None
    """
    @staticmethod
    def fetch_tasks(query_params: Dict[str, Any]) -> Sequence[Dict[str, Any]]:
        """
        Получить все задачи по параметрам запроса.
        :param query_params: Параметры запроса для фильтрации задач
        :return: Список задач, соответствующих параметрам запроса
        """
        url = f"{API_DEFAULT_URL}/tasks"
        response = requests.get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_by_id(task_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить задачу по ID.
        :param task_id: ID задачи
        :return: Данные задачи в виде словаря или None, если задача не найдена
        """
        url = f"{API_DEFAULT_URL}/tasks/{task_id}"
        response = requests.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    @staticmethod
    def create(max_user_id: int, prompt: str, category_id: int = None) -> None:
        """
        Начать генерацию задачи.
        :param max_user_id:
        :param prompt:
        :param category_id:
        :return: None
        """
        url = f"{API_DEFAULT_URL}/tasks/generate"
        task_data = {
            "max_user_id": max_user_id,
            "prompt": prompt,
            "category_id": category_id
        }
        response = requests.post(url, json=task_data)
        response.raise_for_status()

    @staticmethod
    def rename(task_id: int, new_title: str) -> Dict[str, Any]:
        """
        Переименовать задачу.
        :param task_id: ID задачи
        :param new_title: Новое название задачи
        :return: Данные обновленной задачи в виде словаря
        """
        url = f"{API_DEFAULT_URL}/tasks/{task_id}"
        update_data = {"title": new_title}
        response = requests.patch(url, json=update_data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def rename_description(task_id: int, new_description: str) -> Dict[str, Any]:
        """
        Обновить описание задачи.
        :param task_id: ID задачи
        :param new_description: Новое описание задачи
        :return: Данные обновленной задачи в виде словаря
        """
        url = f"{API_DEFAULT_URL}/tasks/{task_id}"
        update_data = {"description": new_description}
        response = requests.patch(url, json=update_data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def delete(task_id: int) -> None:
        """
        Удалить задачу по ID.
        :param task_id: ID задачи
        """
        url = f"{API_DEFAULT_URL}/tasks/{task_id}"
        response = requests.delete(url)
        response.raise_for_status()

task_service = TaskService()