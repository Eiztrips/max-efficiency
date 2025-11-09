import pytest
from app.services.category import CategoryService
from app.models import User, Category, Task, Tag


class TestCategoryService:
    """Тесты для CategoryService"""

    @pytest.mark.asyncio
    async def test_create_category(self, db_session):
        """Тест создания категории"""
        user = User(max_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create_category(user.id, "Test Category", "Test Description")

        assert category is not None
        assert category.name == "Test Category"
        assert category.description == "Test Description"
        assert category.owner_id == user.id

    @pytest.mark.asyncio
    async def test_create_category_invalid_user_id(self, db_session):
        """Тест создания категории с невалидным user_id"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.create_category(-1, "Test Category")

        with pytest.raises(ValueError, match="ID пользователя должен быть положительным целым числом"):
            await service.create_category(0, "Test Category")

    @pytest.mark.asyncio
    async def test_create_category_invalid_name(self, db_session):
        """Тест создания категории с невалидным названием"""
        user = User(max_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="название категории должен быть непустой строкой"):
            await service.create_category(user.id, "")

        with pytest.raises(ValueError, match="название категории должен быть непустой строкой"):
            await service.create_category(user.id, "   ")

    @pytest.mark.asyncio
    async def test_patch_category(self, db_session):
        """Тест обновления категории"""
        user = User(max_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create_category(user.id, "Old Name", "Old Description")

        updated_category = await service.patch_category(category.id, {"name": "New Name"})

        assert updated_category is not None
        assert updated_category.name == "New Name"
        assert updated_category.description == "Old Description"

    @pytest.mark.asyncio
    async def test_patch_category_not_found(self, db_session):
        """Тест обновления несуществующей категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="Категория не найдена"):
            await service.patch_category(999, {"name": "New Name"})

    @pytest.mark.asyncio
    async def test_patch_category_invalid_id(self, db_session):
        """Тест обновления категории с невалидным ID"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.patch_category(-1, {"name": "New Name"})

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.patch_category(0, {"name": "New Name"})

    @pytest.mark.asyncio
    async def test_patch_category_empty_data(self, db_session):
        """Тест обновления категории с пустыми данными"""
        user = User(max_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create_category(user.id, "Test Category")

        with pytest.raises(ValueError, match="данные для обновления категории должен быть непустым словарем"):
            await service.patch_category(category.id, {})

    @pytest.mark.asyncio
    async def test_patch_category_constant_fields(self, db_session):
        """Тест обновления неизменяемых полей категории"""
        user = User(max_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create_category(user.id, "Test Category")

        with pytest.raises(ValueError, match="Нельзя изменять поле: id"):
            await service.patch_category(category.id, {"id": 999})

        with pytest.raises(ValueError, match="Нельзя изменять поле: owner_id"):
            await service.patch_category(category.id, {"owner_id": 999})

    @pytest.mark.asyncio
    async def test_delete_category(self, db_session):
        """Тест удаления категории"""
        user = User(max_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = CategoryService(db_session)
        category = await service.create_category(user.id, "Test Category")

        result = await service.delete_category(category.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, db_session):
        """Тест удаления несуществующей категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="Категория не найдена"):
            await service.delete_category(999)

    @pytest.mark.asyncio
    async def test_delete_category_invalid_id(self, db_session):
        """Тест удаления категории с невалидным ID"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.delete_category(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.delete_category(0)

    @pytest.mark.asyncio
    async def test_get_all_users_by_category_id(self, db_session):
        """Тест получения всех пользователей категории"""
        from app.repositories.category import CategoryRepository

        user1 = User(max_id=123456, username="user1")
        user2 = User(max_id=123457, username="user2")
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
        users = await service.get_all_users_by_category_id(category.id)

        assert len(users) == 2
        assert all(isinstance(u, User) for u in users)

    @pytest.mark.asyncio
    async def test_get_all_users_by_category_id_invalid_id(self, db_session):
        """Тест получения пользователей с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_all_users_by_category_id(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_all_users_by_category_id(0)

    @pytest.mark.asyncio
    async def test_get_all_tags_by_category_id(self, db_session):
        """Тест получения всех тегов категории"""
        user = User(max_id=123456, username="test_user")
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
        tags = await service.get_all_tags_by_category_id(category.id)

        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)

    @pytest.mark.asyncio
    async def test_get_all_tags_by_category_id_invalid_id(self, db_session):
        """Тест получения тегов с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_all_tags_by_category_id(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_all_tags_by_category_id(0)

    @pytest.mark.asyncio
    async def test_get_all_tasks_by_category_id(self, db_session):
        """Тест получения всех задач категории"""
        user = User(max_id=123456, username="test_user")
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
        tasks = await service.get_all_tasks_by_category_id(category.id)

        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)

    @pytest.mark.asyncio
    async def test_get_all_tasks_by_category_id_invalid_id(self, db_session):
        """Тест получения задач с невалидным ID категории"""
        service = CategoryService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_all_tasks_by_category_id(-1)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.get_all_tasks_by_category_id(0)

