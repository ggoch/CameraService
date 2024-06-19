import pytest
from redis_om import get_redis_connection

from typing import Optional
from redis_om import HashModel, Field
from redis_om import Migrator

REDIS_URL = "redis://localhost:6379"

redis = get_redis_connection(url=REDIS_URL)

Migrator().run()


class UserReadCache(HashModel):
    id: int = Field(index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    avatar: Optional[str] = None

    class Meta:
        database = redis


def test_create_user():
    new_user = UserReadCache(
        id=1, name="json_user", email="json_user@email.com", avatar="image_url"
    )
    new_user.save()  # <--- 透過 save 來存入資料
    pk = new_user.pk  # <--- 取得 primary key
    assert UserReadCache.get(pk) == new_user  # <--- 透過 get 來取得資料


# 使用redis/redis-stack:lastest即可解決問題。
# 但考慮到abp使用的是redis所以暫不考慮此方法。
# def test_find_user_hash():
#     user_be_found = UserReadCache(
#         id=1, name="json_user", email="json_user@email.com", avatar="image_url"
#     )
#     result = UserReadCache.find(
#         UserReadCache.id == 1
#     ).first()  # <--- 透過 find 來查詢資料
#     assert result.id == user_be_found.id
#     assert result.name == user_be_found.name
