import random
import pytest
import json
from functools import lru_cache

from tests.conftest import async_session

@lru_cache()
def get_user_data():
    with open("data/user_data.json") as f:
        data = json.load(f)
    return data

def get_random_user():
    return [ random.choice(get_user_data()) ]

async def get_user_id(async_client,user):
    response = await async_client.get(f"/api/users?last=0&limit=50&keyword={user['name']}")
    print(response.json())
    assert response.status_code == 200
    return response.json()[0]["id"]

@pytest.mark.parametrize("user",get_user_data())
@pytest.mark.asyncio
async def test_create_user(async_client,user):
    response = await async_client.post("/api/users",json=user)

    assert response.status_code == 201
    assert response.json()["name"] == user["name"]
    assert response.json()["email"] == user["email"]
    assert response.json()["id"] == await get_user_id(async_client,user)