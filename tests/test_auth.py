import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Register
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User", "role": "admin"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    
    # 2. Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]
    
    # 3. Use token
    response = await client.get(
        "/api/v1/records/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
