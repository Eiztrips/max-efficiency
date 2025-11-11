import pytest
from datetime import datetime, timedelta

from app.services.task import TaskService
from app.repositories.user import UserRepository
from app.repositories.category import CategoryRepository
from app.schemas import TaskCreate
from app.schemas.task import TaskQuery, TaskUpdate


class TestTaskService:

    @pytest.mark.asyncio
    async def test_get_tasks(self, db_session):
        """Тест получения задач пользователя"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_user_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        payload1 = TaskCreate(
            user_id=user.id,
            title="Task 1",
            description="Description 1",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )
        await service.create(payload1)

        payload2 = TaskCreate(
            user_id=user.id,
            title="Task 2",
            description="Description 2",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )
        await service.create(payload2)

        query = TaskQuery(user_id=user.id)
        tasks = await service.get_tasks(query)

        assert len(tasks) == 2
        assert all(task.user_id == user.id for task in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_with_filters(self, db_session):
        """Тест получения задач с фильтрами
        :arg category_id: фильтр по категории
        :arg is_completed: фильтр по статусу выполнения
        """
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_user_id=123456, username="test_user")
        category1 = await category_repo.create(name="Work", description="", user_id=user.id)
        category2 = await category_repo.create(name="Home", description="", user_id=user.id)

        payload1 = TaskCreate(user_id=user.id, title="Work Task", description="sdelat chtoto", expiration_date=None,
                              is_completed=False, category_id=category1.id)
        await service.create(payload1)

        payload2 = TaskCreate(user_id=user.id, title="Home Task", description="pypki sdelai ee", expiration_date=None,
                              is_completed=True, category_id=category2.id)
        await service.create(payload2)

        query = TaskQuery(user_id=user.id, category_id=category1.id, is_completed=False)
        tasks = await service.get_tasks(query)

        assert len(tasks) == 1
        assert tasks[0].title == "Work Task"

    @pytest.mark.asyncio
    async def test_get_tasks_with_search(self, db_session):
        """Тест поиска задач"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_user_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        payload1 = TaskCreate(user_id=user.id, title="Important Meeting", description="Discuss project",
                              expiration_date=None, is_completed=False, category_id=category.id)
        await service.create(payload1)

        payload2 = TaskCreate(user_id=user.id, title="Regular Task", description="Some work",
                              expiration_date=None, is_completed=False, category_id=category.id)
        await service.create(payload2)

        query = TaskQuery(user_id=user.id, search="meeting")
        tasks = await service.get_tasks(query)

        assert len(tasks) == 1
        assert tasks[0].title == "Important Meeting"

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Тест создания задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_user_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        expiration = (datetime.now() + timedelta(days=7))

        payload = TaskCreate(
            user_id=user.id,
            title="New Task",
            description="Task description",
            expiration_date=expiration,
            is_completed=False,
            category_id=category.id
        )
        task = await service.create(payload)

        assert task is not None
        assert task.id is not None
        assert task.title == "New Task"
        assert task.description == "Task description"
        assert task.user_id == user.id
        assert task.category_id == category.id
        assert task.is_completed is False


    @pytest.mark.asyncio
    async def test_patch(self, db_session):
        """Тест обновления задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_user_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        payload = TaskCreate(
            user_id=user.id,
            title="Old Title",
            description="Old Description",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )
        task = await service.create(payload)

        update_payload = TaskUpdate(
            id=task.id,
            title="New Title",
            is_completed=True
        )
        updated_task = await service.patch(update_payload)

        assert updated_task is not None
        assert updated_task.id == task.id
        assert updated_task.title == "New Title"
        assert updated_task.is_completed is True
        assert updated_task.description == "Old Description"

    @pytest.mark.asyncio
    async def test_patch_not_found(self, db_session):
        """Тест обновления несуществующей задачи"""
        service = TaskService(db_session)

        update_payload = TaskUpdate(id=999, title="New Title")
        result = await service.patch(update_payload)

        assert result is None


    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """Тест удаления задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_user_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        payload = TaskCreate(
            user_id=user.id,
            title="Task to delete",
            description="Description",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )
        task = await service.create(payload)
        await service.delete(task.id)
        result = await service.get_by_id(task.id)

        assert result is None