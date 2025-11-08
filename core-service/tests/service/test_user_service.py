import pytest
from app.services.user import UserService
from app.models import User, Category, Task


class TestUserService:
    """Тесты для UserService"""

    @pytest.mark.asyncio
    async def test_get_user_by_max_id(self, db_session):
        """Тест получения пользователя по max_id"""
        service = UserService(db_session)
        await service.get_or_create_user(max_id=123456, username="test_user")
        user = await service.get_user_by_max_id(123456)

        assert user is not None
        assert user.max_id == 123456
        assert user.username == "test_user"

    @pytest.mark.asyncio
    async def test_get_user_by_max_id_not_found(self, db_session):
        """Тест получения несуществующего пользователя"""
        service = UserService(db_session)

        user = await service.get_user_by_max_id(999999)

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_max_id_invalid_value(self, db_session):
        """Тест с невалидным max_id"""
        service = UserService(db_session)

        with pytest.raises(ValueError, match="max_id пользователя должен быть положительным целым числом"):
            await service.get_user_by_max_id(-1)

        with pytest.raises(ValueError, match="max_id пользователя должен быть положительным целым числом"):
            await service.get_user_by_max_id(0)

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session):
        """Тест получения пользователя по username"""
        service = UserService(db_session)

        await service.get_or_create_user(max_id=123456, username="test_user")

        user = await service.get_user_by_username("test_user")

        assert user is not None
        assert user.username == "test_user"
        assert user.max_id == 123456

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session):
        """Тест получения несуществующего пользователя по username"""
        service = UserService(db_session)

        user = await service.get_user_by_username("nonexistent_user")

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_invalid_value(self, db_session):
        """Тест с невалидным username"""
        service = UserService(db_session)

        with pytest.raises(ValueError, match="username пользователя должен быть непустой строкой"):
            await service.get_user_by_username("")

        with pytest.raises(ValueError, match="username пользователя должен быть непустой строкой"):
            await service.get_user_by_username("   ")

    @pytest.mark.asyncio
    async def test_get_or_create_user_creates_new(self, db_session):
        """Тест создания нового пользователя"""
        service = UserService(db_session)

        user = await service.get_or_create_user(max_id=123456, username="new_user")

        assert user is not None
        assert user.max_id == 123456
        assert user.username == "new_user"
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_get_or_create_user_returns_existing(self, db_session):
        """Тест возврата существующего пользователя"""
        service = UserService(db_session)

        user1 = await service.get_or_create_user(max_id=123456, username="test_user")

        user2 = await service.get_or_create_user(max_id=123456, username="another_name")

        assert user1.id == user2.id
        assert user2.max_id == 123456
        assert user2.username == "test_user"

    @pytest.mark.asyncio
    async def test_get_or_create_user_invalid_values(self, db_session):
        """Тест с невалидными значениями"""
        service = UserService(db_session)

        with pytest.raises(ValueError, match="max_id пользователя должен быть положительным целым числом"):
            await service.get_or_create_user(max_id=-1, username="test")

        with pytest.raises(ValueError, match="username пользователя должен быть непустой строкой"):
            await service.get_or_create_user(max_id=123, username="")

    @pytest.mark.asyncio
    async def test_patch_user(self, db_session):
        """Тест обновления пользователя"""
        service = UserService(db_session)

        user = await service.get_or_create_user(max_id=123456, username="old_name")

        updated_user = await service.patch_user(user.id, {"username": "new_name"})

        assert updated_user is not None
        assert updated_user.username == "new_name"
        assert updated_user.max_id == 123456

    @pytest.mark.asyncio
    async def test_patch_user_not_found(self, db_session):
        """Тест обновления несуществующего пользователя"""
        service = UserService(db_session)

        result = await service.patch_user(999, {"username": "new_name"})

        assert result is None

    @pytest.mark.asyncio
    async def test_patch_user_invalid_values(self, db_session):
        """Тест обновления с невалидными значениями"""
        service = UserService(db_session)

        user = await service.get_or_create_user(max_id=123456, username="test_user")

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.patch_user(-1, {"username": "new_name"})

        with pytest.raises(ValueError, match="данные для обновления пользователя должен быть непустым словарем"):
            await service.patch_user(user.id, {})

        with pytest.raises(ValueError, match="Нельзя изменять поле: id"):
            await service.patch_user(user.id, {"id": 999})

        with pytest.raises(ValueError, match="Нельзя изменять поле: max_id"):
            await service.patch_user(user.id, {"max_id": 999999})

    @pytest.mark.asyncio
    async def test_get_user_categories(self, db_session):
        """Тест получения категорий пользователя"""
        service = UserService(db_session)

        user = await service.get_or_create_user(max_id=123456, username="test_user")

        category1 = Category(name="Category 1", description="Desc 1", owner_id=user.id)
        category2 = Category(name="Category 2", description="Desc 2", owner_id=user.id)
        db_session.add(category1)
        db_session.add(category2)
        await db_session.commit()

        categories = await service.get_user_categories(123456)

        assert len(categories) == 2
        assert all(isinstance(c, Category) for c in categories)

    @pytest.mark.asyncio
    async def test_get_user_tasks(self, db_session):
        """Тест получения задач пользователя"""
        service = UserService(db_session)

        user = await service.get_or_create_user(max_id=123456, username="test_user")

        category = Category(name="Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        task1 = Task(user_id=user.id, title="Task 1", category_id=category.id)
        task2 = Task(user_id=user.id, title="Task 2", category_id=category.id)
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()

        tasks = await service.get_user_tasks(123456)

        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)

    @pytest.mark.asyncio
    async def test_get_user_tags(self, db_session):
        """Тест получения тегов пользователя"""
        service = UserService(db_session)

        user = await service.get_or_create_user(max_id=123456, username="test_user")

        category = Category(name="Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        from app.models import Tag
        tag1 = Tag(name="Tag 1", color="red", category_id=category.id)
        tag2 = Tag(name="Tag 2", color="blue", category_id=category.id)
        db_session.add(tag1)
        db_session.add(tag2)
        await db_session.commit()

        tags = await service.get_user_tags(123456)

        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)

