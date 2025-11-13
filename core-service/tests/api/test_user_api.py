import pytest
from httpx import AsyncClient


class TestUserAPI:
    """Тесты для API пользователей"""

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient):
        """Тест создания нового пользователя"""
        payload = {
            "max_user_id": 12345,
            "username": "testuser"
        }

        response = await client.post("/api/v1/users", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["max_user_id"] == 12345
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_user_without_username(self, client: AsyncClient):
        """Тест создания пользователя без username"""
        payload = {
            "max_user_id": 12346
        }

        response = await client.post("/api/v1/users", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["max_user_id"] == 12346
        assert data["username"] is None

    @pytest.mark.asyncio
    async def test_get_or_create_existing_user(self, client: AsyncClient):
        """Тест получения существующего пользователя (get_or_create)"""
        payload = {
            "max_user_id": 12347,
            "username": "existinguser"
        }

        response1 = await client.post("/api/v1/users", json=payload)
        assert response1.status_code == 201
        user1_id = response1.json()["id"]

        response2 = await client.post("/api/v1/users", json=payload)
        assert response2.status_code == 201
        user2_id = response2.json()["id"]

        assert user1_id == user2_id

    @pytest.mark.asyncio
    async def test_get_user_by_max_user_id(self, client: AsyncClient):
        """Тест получения пользователя по max_user_id"""
        payload = {
            "max_user_id": 12348,
            "username": "getuser"
        }
        create_response = await client.post("/api/v1/users", json=payload)
        assert create_response.status_code == 201

        response = await client.get("/api/v1/users/12348")

        assert response.status_code == 200
        data = response.json()
        assert data["max_user_id"] == 12348
        assert data["username"] == "getuser"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, client: AsyncClient):
        """Тест получения несуществующего пользователя"""
        response = await client.get("/api/v1/users/99999")

        assert response.status_code in [400, 404]
        assert "не найден" in response.json()["detail"] or "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_all_users(self, client: AsyncClient):
        """Тест получения всех пользователей (DEBUG endpoint)"""
        for i in range(3):
            payload = {
                "max_user_id": 10000 + i,
                "username": f"user{i}"
            }
            await client.post("/api/v1/users", json=payload)

        response = await client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_get_user_categories(self, client: AsyncClient):
        """Тест получения категорий пользователя"""
        user_payload = {
            "max_user_id": 12349,
            "username": "categoryuser"
        }
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {
            "max_user_id": 12349,
            "name": "Test Category",
            "description": "Test Description"
        }
        await client.post("/api/v1/categories", json=category_payload)

        response = await client.get("/api/v1/users/user/12349/categories")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "test category"

    @pytest.mark.asyncio
    async def test_get_user_tags(self, client: AsyncClient):
        """Тест получения тегов пользователя"""
        user_payload = {
            "max_user_id": 12350,
            "username": "taguser"
        }
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {
            "max_user_id": 12350,
            "name": "Tag Category",
            "description": "For tags"
        }
        cat_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = cat_response.json()["id"]

        tag_payload = {
            "category_id": category_id,
            "name": "Test Tag",
            "color": "#FF0000"
        }
        await client.post("/api/v1/tags", json=tag_payload)

        response = await client.get("/api/v1/users/user/12350/tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Test Tag"
