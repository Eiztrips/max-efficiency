import pytest
from app.services.category import CategoryService
from app.models import User, Category, Task, Tag


class TestCategoryService:
    """Тесты для CategoryService"""

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Тест создания категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create(user.id, "Test Category", "Test Description")

        assert category is not None
        assert category.name == "Test Category"
        assert category.description == "Test Description"
        assert category.owner_id == user.id

    @pytest.mark.asyncio
    async def test_create_invalid_user_id(self, db_session):
        """Тест создания категории с невалидным user_id"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.create(-1, "Test Category")

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.create(0, "Test Category")

    @pytest.mark.asyncio
    async def test_create_invalid_name(self, db_session):
        """Тест создания категории с невалидным названием"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="название категории должен быть непустой строкой"):
            await service.create(user.id, "")

        with pytest.raises(ValueError, match="название категории должен быть непустой строкой"):
            await service.create(user.id, "   ")

    @pytest.mark.asyncio
    async def test_add_user(self, db_session):
        """Тест добавления пользователя в категорию через сервис"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create(user.id, "Test Category")

        repo = service.category_repo
        result = await repo.add_user(category.id, user.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_add_user_invalid_ids(self, db_session):
        """Тест добавления пользователя с невалидными ID"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.add_user(-1, 1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.add_user(0, 1)

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.add_user(1, -1)

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.add_user(1, 0)

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """Тест удаления категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create(user.id, "Test Category")

        result = await service.delete(category.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """Тест удаления несуществующей категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="Категория не найдена"):
            await service.delete(999)

    @pytest.mark.asyncio
    async def test_delete_invalid_id(self, db_session):
        """Тест удаления категории с невалидным ID"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.delete(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.delete(0)

    @pytest.mark.asyncio
    async def test_get_all_users_by_category_id(self, db_session):
        """Тест получения всех пользователей категории"""
        from app.repositories.category import CategoryRepository

        user1 = User(max_user_id=123456, username="user1")
        user2 = User(max_user_id=123457, username="user2")
        db_session.add(user1)
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)

        category = Category(name="Test Category", description="Desc", owner_id=user1.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = CategoryRepository(db_session)
        await repo.add_user(category.id, user1.id)
        await repo.add_user(category.id, user2.id)

        service = CategoryService(db_session)
        users = await service.get_users_by_category_id(category.id)

        assert len(users) == 2
        assert all(isinstance(u, User) for u in users)

    @pytest.mark.asyncio
    async def test_get_all_users_by_category_id_invalid_id(self, db_session):
        """Тест получения пользователей с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_users_by_category_id(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_users_by_category_id(0)

    @pytest.mark.asyncio
    async def test_get_all_tags_by_category_id(self, db_session):
        """Тест получения всех тегов категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(name="Test Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        tag1 = Tag(name="Tag 1", color="red", category_id=category.id)
        tag2 = Tag(name="Tag 2", color="blue", category_id=category.id)
        db_session.add(tag1)
        db_session.add(tag2)
        await db_session.commit()

        service = CategoryService(db_session)
        tags = await service.get_tags_by_category_id(category.id)

        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)

    @pytest.mark.asyncio
    async def test_get_all_tags_by_category_id_invalid_id(self, db_session):
        """Тест получения тегов с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_tags_by_category_id(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_tags_by_category_id(0)

    @pytest.mark.asyncio
    async def test_get_all_tasks_by_category_id(self, db_session):
        """Тест получения всех задач категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(name="Test Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        task1 = Task(user_id=user.id, title="Task 1", category_id=category.id)
        task2 = Task(user_id=user.id, title="Task 2", category_id=category.id)
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()

        service = CategoryService(db_session)
        tasks = await service.get_tasks_by_category_id(category.id)

        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)

    @pytest.mark.asyncio
    async def test_get_all_tasks_by_category_id_invalid_id(self, db_session):
        """Тест получения задач с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_tasks_by_category_id(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_tasks_by_category_id(0)

