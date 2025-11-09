import pytest
from datetime import datetime, timedelta
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.repositories.category import CategoryRepository
from app.repositories.tag import TagRepository


class TestTaskRepository:

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session):
        """Тест получения задачи по ID"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="Work tasks", user_id=user.id)
        task = await task_repo.create(
            user_id=user.id,
            title="Test Task",
            description="Test Description",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )

        result = await task_repo.get_by_id(task.id)

        assert result is not None
        assert result.id == task.id
        assert result.title == "Test Task"
        assert result.user_id == user.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """Тест получения несуществующей задачи"""
        task_repo = TaskRepository(db_session)
        result = await task_repo.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_by_user_id(self, db_session):
        """Тест получения всех задач пользователя"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user1 = await user_repo.create(max_id=123456, username="user1")
        user2 = await user_repo.create(max_id=789012, username="user2")
        category = await category_repo.create(name="Work", description="", user_id=user1.id)

        await task_repo.create(user_id=user1.id, title="Task 1", description="", expiration_date=None,
                               is_completed=False, category_id=category.id)
        await task_repo.create(user_id=user1.id, title="Task 2", description="", expiration_date=None,
                               is_completed=False, category_id=category.id)
        await task_repo.create(user_id=user2.id, title="Task 3", description="", expiration_date=None,
                               is_completed=False, category_id=category.id)

        result = await task_repo.get_all_by_user_id(user1.id)

        assert len(result) == 2
        assert all(task.user_id == user1.id for task in result)

    @pytest.mark.asyncio
    async def test_get_tasks_by_category(self, db_session):
        """Тест фильтрации задач по категории"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category1 = await category_repo.create(name="Work", description="", user_id=user.id)
        category2 = await category_repo.create(name="Home", description="", user_id=user.id)

        await task_repo.create(user_id=user.id, title="Work Task", description="", expiration_date=None,
                               is_completed=False, category_id=category1.id)
        await task_repo.create(user_id=user.id, title="Home Task", description="", expiration_date=None,
                               is_completed=False, category_id=category2.id)

        result = await task_repo.get_tasks(user_id=user.id, category_id=category1.id)

        assert len(result) == 1
        assert result[0].title == "Work Task"
        assert result[0].category_id == category1.id

    @pytest.mark.asyncio
    async def test_get_tasks_by_tag(self, db_session):
        """Тест фильтрации задач по тегу"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        tag_repo = TagRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        tag = await tag_repo.create(name="urgent", color="red", category_id=category.id)

        task1 = await task_repo.create(user_id=user.id, title="Urgent Task", description="", expiration_date=None,
                                       is_completed=False, category_id=category.id)
        task2 = await task_repo.create(user_id=user.id, title="Regular Task", description="", expiration_date=None,
                                       is_completed=False, category_id=category.id)

        from sqlalchemy import insert
        from app.models import task_tags

        stmt = insert(task_tags).values(task_id=task1.id, tag_id=tag.id)
        await db_session.execute(stmt)
        await db_session.commit()

        result = await task_repo.get_tasks(user_id=user.id, tag_id=tag.id)

        assert len(result) == 1
        assert result[0].title == "Urgent Task"

    @pytest.mark.asyncio
    async def test_get_tasks_by_completion_status(self, db_session):
        """Тест фильтрации задач по статусу завершения"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        await task_repo.create(user_id=user.id, title="Completed Task", description="", expiration_date=None,
                               is_completed=True, category_id=category.id)
        await task_repo.create(user_id=user.id, title="Pending Task", description="", expiration_date=None,
                               is_completed=False, category_id=category.id)

        result = await task_repo.get_tasks(user_id=user.id, is_completed=True)

        assert len(result) == 1
        assert result[0].title == "Completed Task"
        assert result[0].is_completed is True

    @pytest.mark.asyncio
    async def test_get_tasks_by_date_range(self, db_session):
        """Тест фильтрации задач по диапазону дат"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        date1 = datetime.now() + timedelta(days=1)
        date2 = datetime.now() + timedelta(days=5)
        date3 = datetime.now() + timedelta(days=10)

        await task_repo.create(user_id=user.id, title="Task 1", description="", expiration_date=date1,
                               is_completed=False, category_id=category.id)
        await task_repo.create(user_id=user.id, title="Task 2", description="", expiration_date=date2,
                               is_completed=False, category_id=category.id)
        await task_repo.create(user_id=user.id, title="Task 3", description="", expiration_date=date3,
                               is_completed=False, category_id=category.id)

        from_date = (datetime.now() + timedelta(days=2)).isoformat()
        to_date = (datetime.now() + timedelta(days=7)).isoformat()

        result = await task_repo.get_tasks(user_id=user.id, from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert result[0].title == "Task 2"

    @pytest.mark.asyncio
    async def test_get_tasks_by_search(self, db_session):
        """Тест поиска задач по тексту"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        await task_repo.create(user_id=user.id, title="Important Meeting", description="Discuss project",
                               expiration_date=None, is_completed=False, category_id=category.id)
        await task_repo.create(user_id=user.id, title="Regular Task", description="Some work",
                               expiration_date=None, is_completed=False, category_id=category.id)

        result = await task_repo.get_tasks(user_id=user.id, search="meeting")

        assert len(result) == 1
        assert result[0].title == "Important Meeting"

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Тест создания задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        expiration = datetime.now() + timedelta(days=7)

        task = await task_repo.create(
            user_id=user.id,
            title="New Task",
            description="Task description",
            expiration_date=expiration,
            is_completed=False,
            category_id=category.id
        )

        assert task.id is not None
        assert task.title == "New Task"
        assert task.description == "Task description"
        assert task.user_id == user.id
        assert task.category_id == category.id
        assert task.is_completed is False
        assert task.created_at is not None

    @pytest.mark.asyncio
    async def test_patch(self, db_session):
        """Тест обновления задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        task = await task_repo.create(
            user_id=user.id,
            title="Old Title",
            description="Old Description",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )

        updated_task = await task_repo.patch(task.id, {
            "title": "New Title",
            "is_completed": True
        })

        assert updated_task is not None
        assert updated_task.id == task.id
        assert updated_task.title == "New Title"
        assert updated_task.is_completed is True
        assert updated_task.description == "Old Description"

    @pytest.mark.asyncio
    async def test_patch_not_found(self, db_session):
        """Тест обновления несуществующей задачи"""
        task_repo = TaskRepository(db_session)
        result = await task_repo.patch(999, {"title": "New Title"})

        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """Тест удаления задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        task_repo = TaskRepository(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        task = await task_repo.create(
            user_id=user.id,
            title="Task to delete",
            description="",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )

        result = await task_repo.delete(task.id)

        assert result is True
        deleted_task = await task_repo.get_by_id(task.id)
        assert deleted_task is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """Тест удаления несуществующей задачи"""
        task_repo = TaskRepository(db_session)
        result = await task_repo.delete(999)

        assert result is False
