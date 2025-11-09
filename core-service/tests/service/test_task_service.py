import pytest
from datetime import datetime, timedelta
from app.services.task import TaskService
from app.repositories.user import UserRepository
from app.repositories.category import CategoryRepository
from app.repositories.tag import TagRepository


class TestTaskService:

    @pytest.mark.asyncio
    async def test_get_tasks(self, db_session):
        """Тест получения задач пользователя"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        await service.create_task(
            user_id=user.id,
            title="Task 1",
            description="Description 1",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )
        await service.create_task(
            user_id=user.id,
            title="Task 2",
            description="Description 2",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )

        tasks = await service.get_tasks(user_id=user.id)

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

        user = await user_repo.create(max_id=123456, username="test_user")
        category1 = await category_repo.create(name="Work", description="", user_id=user.id)
        category2 = await category_repo.create(name="Home", description="", user_id=user.id)

        await service.create_task(user_id=user.id, title="Work Task", description="sdelat chtoto", expiration_date=None,
                                  is_completed=False, category_id=category1.id)
        await service.create_task(user_id=user.id, title="Home Task", description="pypki sdelai ee", expiration_date=None,
                                  is_completed=True, category_id=category2.id)

        tasks = await service.get_tasks(user_id=user.id, category_id=category1.id, is_completed=False)

        assert len(tasks) == 1
        assert tasks[0].title == "Work Task"

    @pytest.mark.asyncio
    async def test_get_tasks_with_search(self, db_session):
        """Тест поиска задач"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)

        await service.create_task(user_id=user.id, title="Important Meeting", description="Discuss project",
                                  expiration_date=None, is_completed=False, category_id=category.id)
        await service.create_task(user_id=user.id, title="Regular Task", description="Some work",
                                  expiration_date=None, is_completed=False, category_id=category.id)

        tasks = await service.get_tasks(user_id=user.id, search="meeting")

        assert len(tasks) == 1
        assert tasks[0].title == "Important Meeting"

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_user_id(self, db_session):
        """Тест с невалидным user_id"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.get_tasks(user_id=-1)

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.get_tasks(user_id=0)

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_category_id(self, db_session):
        """Тест с невалидным category_id"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_tasks(user_id=1, category_id=-1)

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_tag_id(self, db_session):
        """Тест с невалидным tag_id"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="ID тега должен быть положительным целым числом"):
            await service.get_tasks(user_id=1, tag_id=0)

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_status(self, db_session):
        """Тест с невалидным статусом"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="статус задачи должен быть непустой строкой"):
            await service.get_tasks(user_id=1, status="")

        with pytest.raises(ValueError, match="статус задачи должен быть непустой строкой"):
            await service.get_tasks(user_id=1, status="   ")

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_dates(self, db_session):
        """Тест с невалидными датами"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="дата начала диапазона должен быть непустой строкой"):
            await service.get_tasks(user_id=1, from_date="")

        with pytest.raises(ValueError, match="дата конца диапазона должен быть непустой строкой"):
            await service.get_tasks(user_id=1, to_date="   ")

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_search(self, db_session):
        """Тест с невалидным поисковым запросом"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="поисковый запрос должен быть непустой строкой"):
            await service.get_tasks(user_id=1, search="")

    @pytest.mark.asyncio
    async def test_create_task(self, db_session):
        """Тест создания задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        expiration = (datetime.now() + timedelta(days=7))

        task = await service.create_task(
            user_id=user.id,
            title="New Task",
            description="Task description",
            expiration_date=expiration,
            is_completed=False,
            category_id=category.id
        )

        assert task is not None
        assert task.id is not None
        assert task.title == "New Task"
        assert task.description == "Task description"
        assert task.user_id == user.id
        assert task.category_id == category.id
        assert task.is_completed is False

    @pytest.mark.asyncio
    async def test_create_task_invalid_user_id(self, db_session):
        """Тест создания задачи с невалидным user_id"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.create_task(user_id=-1, title="Task", description="Desc",
                                      expiration_date=None, is_completed=False, category_id=1)

    @pytest.mark.asyncio
    async def test_create_task_invalid_title(self, db_session):
        """Тест создания задачи с невалидным названием"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="название задачи должен быть непустой строкой"):
            await service.create_task(user_id=1, title="", description="Desc",
                                      expiration_date=None, is_completed=False, category_id=1)

        with pytest.raises(ValueError, match="название задачи должен быть непустой строкой"):
            await service.create_task(user_id=1, title="   ", description="Desc",
                                      expiration_date=None, is_completed=False, category_id=1)

    @pytest.mark.asyncio
    async def test_create_task_invalid_description(self, db_session):
        """Тест создания задачи с невалидным описанием"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="описание задачи должен быть непустой строкой"):
            await service.create_task(user_id=1, title="Task", description="",
                                      expiration_date=None, is_completed=False, category_id=1)

    @pytest.mark.asyncio
    async def test_create_task_invalid_category_id(self, db_session):
        """Тест создания задачи с невалидным category_id"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.create_task(user_id=1, title="Task", description="Desc",
                                      expiration_date=None, is_completed=False, category_id=0)

    @pytest.mark.asyncio
    async def test_patch_task(self, db_session):
        """Тест обновления задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        task = await service.create_task(
            user_id=user.id,
            title="Old Title",
            description="Old Description",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )

        updated_task = await service.patch_task(task.id, {
            "title": "New Title",
            "is_completed": True
        })

        assert updated_task is not None
        assert updated_task.id == task.id
        assert updated_task.title == "New Title"
        assert updated_task.is_completed is True
        assert updated_task.description == "Old Description"

    @pytest.mark.asyncio
    async def test_patch_task_not_found(self, db_session):
        """Тест обновления несуществующей задачи"""
        service = TaskService(db_session)

        result = await service.patch_task(999, {"title": "New Title"})

        assert result is None

    @pytest.mark.asyncio
    async def test_patch_task_invalid_id(self, db_session):
        """Тест обновления задачи с невалидным ID"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="ID задачи должен быть положительным целым числом"):
            await service.patch_task(-1, {"title": "New Title"})

    @pytest.mark.asyncio
    async def test_patch_task_invalid_data(self, db_session):
        """Тест обновления задачи с невалидными данными"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="данные для обновления задачи должен быть непустым словарем"):
            await service.patch_task(1, {})

    @pytest.mark.asyncio
    async def test_patch_task_forbidden_fields(self, db_session):
        """Тест попытки изменить запрещенные поля"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        task = await service.create_task(
            user_id=user.id,
            title="Task",
            description="Description",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )

        with pytest.raises(ValueError, match="Нельзя изменять поле: id"):
            await service.patch_task(task.id, {"id": 999})

        with pytest.raises(ValueError, match="Нельзя изменять поле: user_id"):
            await service.patch_task(task.id, {"user_id": 999})

    @pytest.mark.asyncio
    async def test_delete_task(self, db_session):
        """Тест удаления задачи"""
        user_repo = UserRepository(db_session)
        category_repo = CategoryRepository(db_session)
        service = TaskService(db_session)

        user = await user_repo.create(max_id=123456, username="test_user")
        category = await category_repo.create(name="Work", description="", user_id=user.id)
        task = await service.create_task(
            user_id=user.id,
            title="Task to delete",
            description="Description",
            expiration_date=None,
            is_completed=False,
            category_id=category.id
        )

        result = await service.delete_task(task.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, db_session):
        """Тест удаления несуществующей задачи"""
        service = TaskService(db_session)

        result = await service.delete_task(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_task_invalid_id(self, db_session):
        """Тест удаления задачи с невалидным ID"""
        service = TaskService(db_session)

        with pytest.raises(ValueError, match="ID задачи должен быть положительным целым числом"):
            await service.delete_task(0)

        with pytest.raises(ValueError, match="ID задачи должен быть положительным целым числом"):
            await service.delete_task(-1)