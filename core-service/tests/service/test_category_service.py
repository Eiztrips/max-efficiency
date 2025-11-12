import pytest
from fastapi import HTTPException
from app.services.category import CategoryService
from app.models import User, Category, Task, Tag
from app.schemas.category import CategoryCreate, CategoryUsersUpdateV2


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
        payload = CategoryCreate(user_id=user.id, name="Test Category", description="Test Description")
        category = await service.create(payload)

        assert category is not None
        assert category.name == "Test Category"
        assert category.description == "Test Description"
        assert category.owner_id == user.id

    @pytest.mark.asyncio
    async def test_add_user(self, db_session):
        """Тест добавления пользователя в категорию через сервис"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await service.create(payload)

        add_user_payload = CategoryUsersUpdateV2(id=category.id, user_id=user.id)
        result = await service.add_user(add_user_payload)

        assert result is not None
        assert result.id == category.id

    @pytest.mark.asyncio
    async def test_add_user_failure(self, db_session):
        """Тест добавления пользователя в несуществующую категорию"""
        service = CategoryService(db_session)

        add_user_payload = CategoryUsersUpdateV2(id=999, user_id=1)
        with pytest.raises(HTTPException) as exc_info:
            await service.add_user(add_user_payload)

        assert exc_info.value.status_code == 400
        assert "Не удалось добавить пользователя в категорию" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """Тест удаления категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await service.create(payload)

        await service.delete(category.id)

        # Проверяем что категория действительно удалена
        deleted_category = await service.get_by_id(category.id)
        assert deleted_category is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """Тест удаления несуществующей категории"""
        service = CategoryService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete(999)

        assert exc_info.value.status_code == 404
        assert "Категория не найдена" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_invalid_id(self, db_session):
        """Тест удаления категории с невалидным ID"""
        service = CategoryService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete(-1)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

        with pytest.raises(HTTPException) as exc_info:
            await service.delete(0)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_joined_users(self, db_session):
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
        await repo.add_user(CategoryUsersUpdateV2(id=category.id, user_id=user1.id))
        await repo.add_user(CategoryUsersUpdateV2(id=category.id, user_id=user2.id))

        service = CategoryService(db_session)
        users = await service.get_joined_users(category.id)

        assert len(users) == 2
        assert all(isinstance(u, User) for u in users)

    @pytest.mark.asyncio
    async def test_get_joined_users_invalid_id(self, db_session):
        """Тест получения пользователей с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_joined_users(-1)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

        with pytest.raises(HTTPException) as exc_info:
            await service.get_joined_users(0)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_tags(self, db_session):
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
        tags = await service.get_tags(category.id)

        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)

    @pytest.mark.asyncio
    async def test_get_tags_invalid_id(self, db_session):
        """Тест получения тегов с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_tags(-1)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

        with pytest.raises(HTTPException) as exc_info:
            await service.get_tags(0)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_tasks(self, db_session):
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
        tasks = await service.get_tasks(category.id)

        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_id(self, db_session):
        """Тест получения задач с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_tasks(-1)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

        with pytest.raises(HTTPException) as exc_info:
            await service.get_tasks(0)

        assert exc_info.value.status_code == 400
        assert "ID категории должен быть положительным целым числом" in exc_info.value.detail

