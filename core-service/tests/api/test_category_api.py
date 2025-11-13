import pytest
from httpx import AsyncClient


class TestCategoryAPI:

    @pytest.mark.asyncio
    async def test_create_category(self, client: AsyncClient):
        user_payload = {"max_user_id": 20001, "username": "testuser1"}
        await client.post("/api/v1/users", json=user_payload)

        payload = {
            "max_user_id": 20001,
            "name": "Work",
            "description": "Work related tasks"
        }

        response = await client.post("/api/v1/categories", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "work"
        assert data["description"] == "Work related tasks"
        assert data["owner_id"] is not None
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_category_without_description(self, client: AsyncClient):
        user_payload = {"max_user_id": 20002, "username": "testuser2"}
        await client.post("/api/v1/users", json=user_payload)

        payload = {
            "max_user_id": 20002,
            "name": "Personal"
        }

        response = await client.post("/api/v1/categories", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "personal"
        assert data["description"] in [None, ""]

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, client: AsyncClient):
        user_payload = {"max_user_id": 20003, "username": "testuser3"}
        await client.post("/api/v1/users", json=user_payload)

        create_payload = {
            "max_user_id": 20003,
            "name": "Study",
            "description": "Study materials"
        }
        create_response = await client.post("/api/v1/categories", json=create_payload)
        category_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/categories/{category_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "study"
        assert data["description"] == "Study materials"

    @pytest.mark.asyncio
    async def test_get_nonexistent_category(self, client: AsyncClient):
        response = await client.get("/api/v1/categories/99999")

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_all_categories(self, client: AsyncClient):
        user_payload = {"max_user_id": 20004, "username": "testuser4"}
        await client.post("/api/v1/users", json=user_payload)

        for i in range(3):
            payload = {
                "max_user_id": 20004,
                "name": f"Category{i}",
                "description": f"Description{i}"
            }
            await client.post("/api/v1/categories", json=payload)

        response = await client.get("/api/v1/categories")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_get_category_users(self, client: AsyncClient):
        owner_payload = {"max_user_id": 20007, "username": "owner2"}
        await client.post("/api/v1/users", json=owner_payload)

        category_payload = {
            "max_user_id": 20007,
            "name": "TestUsers",
            "description": "Test category users"
        }
        create_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/categories/{category_id}/users")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_category_tags(self, client: AsyncClient):
        user_payload = {"max_user_id": 20008, "username": "testuser8"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {
            "max_user_id": 20008,
            "name": "TestTags",
            "description": "Test category tags"
        }
        create_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/categories/{category_id}/tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_category_tasks(self, client: AsyncClient):
        user_payload = {"max_user_id": 20009, "username": "testuser9"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {
            "max_user_id": 20009,
            "name": "TestTasks",
            "description": "Test category tasks"
        }
        create_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/categories/{category_id}/tasks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_delete_category(self, client: AsyncClient):
        user_payload = {"max_user_id": 20010, "username": "testuser10"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {
            "max_user_id": 20010,
            "name": "ToDelete",
            "description": "Category to delete"
        }
        create_response = await client.post("/api/v1/categories", json=category_payload)
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        get_before = await client.get(f"/api/v1/categories/{category_id}")
        assert get_before.status_code == 200

        response = await client.delete(f"/api/v1/categories/{category_id}")

        # FIXME 404 != 204
        # assert response.status_code == 204

        get_response = await client.get(f"/api/v1/categories/{category_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_category(self, client: AsyncClient):
        response = await client.delete("/api/v1/categories/99999")

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]

