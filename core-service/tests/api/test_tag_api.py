import pytest
from httpx import AsyncClient


class TestTagAPI:
    """Тесты для API тегов"""

    @pytest.mark.asyncio
    async def test_create_tag(self, client: AsyncClient):
        """Тест создания нового тега"""
        user_payload = {"max_user_id": 30001, "username": "tagowner"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {
            "max_user_id": 30001,
            "name": "Tag Category"
        }
        cat_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = cat_response.json()["id"]

        tag_payload = {
            "category_id": category_id,
            "name": "Important",
            "color": "#FF0000"
        }

        response = await client.post("/api/v1/tags", json=tag_payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Important"
        assert data["color"] == "#FF0000"
        assert data["category_id"] == category_id
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_tag_with_default_color(self, client: AsyncClient):
        """Тест создания тега с цветом по умолчанию"""
        user_payload = {"max_user_id": 30002, "username": "user2"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {"max_user_id": 30002, "name": "Category"}
        cat_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = cat_response.json()["id"]

        tag_payload = {
            "category_id": category_id,
            "name": "Default Color Tag"
        }

        response = await client.post("/api/v1/tags", json=tag_payload)

        assert response.status_code == 201
        data = response.json()
        assert data["color"] == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_get_tag_by_id(self, client: AsyncClient):
        """Тест получения тега по ID"""
        user_payload = {"max_user_id": 30003, "username": "user3"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {"max_user_id": 30003, "name": "Category"}
        cat_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = cat_response.json()["id"]

        tag_payload = {
            "category_id": category_id,
            "name": "Urgent",
            "color": "#FF5500"
        }
        create_response = await client.post("/api/v1/tags", json=tag_payload)
        tag_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/tags/{tag_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tag_id
        assert data["name"] == "Urgent"
        assert data["color"] == "#FF5500"

    @pytest.mark.asyncio
    async def test_get_nonexistent_tag(self, client: AsyncClient):
        """Тест получения несуществующего тега"""
        response = await client.get("/api/v1/tags/99999")

        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_tag(self, client: AsyncClient):
        """Тест удаления тега"""
        user_payload = {"max_user_id": 30005, "username": "user5"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {"max_user_id": 30005, "name": "Category"}
        cat_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = cat_response.json()["id"]

        tag_payload = {
            "category_id": category_id,
            "name": "To Delete",
            "color": "#000000"
        }
        create_response = await client.post("/api/v1/tags", json=tag_payload)
        tag_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/tags/{tag_id}")

        assert response.status_code == 204

        get_response = await client.get(f"/api/v1/tags/{tag_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_multiple_tags_in_category(self, client: AsyncClient):
        """Тест создания нескольких тегов в одной категории"""
        user_payload = {"max_user_id": 30006, "username": "user6"}
        await client.post("/api/v1/users", json=user_payload)

        category_payload = {"max_user_id": 30006, "name": "Multi Tag Category"}
        cat_response = await client.post("/api/v1/categories", json=category_payload)
        category_id = cat_response.json()["id"]

        tag_names = ["High Priority", "Medium Priority", "Low Priority"]
        colors = ["#FF0000", "#FFA500", "#00FF00"]

        for name, color in zip(tag_names, colors):
            tag_payload = {
                "category_id": category_id,
                "name": name,
                "color": color
            }
            response = await client.post("/api/v1/tags", json=tag_payload)
            assert response.status_code == 201
            assert response.json()["name"] == name
            assert response.json()["color"] == color
