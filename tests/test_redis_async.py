import pytest
import redis.asyncio as redis # <--- 注意這邊是使用 redis.asyncio

REDIS_URL = "redis://localhost:6379"

@pytest.mark.asyncio
async def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)
    value = 'bar_async'
    await redis_connection.set('foo_async', value )
    result = await redis_connection.get('foo_async') # <--- 要使用 await 來取得結果
    redis_connection.close()

    assert result.decode() == value

connection_pool = redis.ConnectionPool.from_url(REDIS_URL)

# ...
@pytest.mark.asyncio
async def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=connection_pool)
    
    value = 'bar_async2'
    await redis_connection.set('foo_async2', value)
    value = await redis_connection.get('foo_async2')
    redis_connection.close()

    assert value.decode() == 'bar_async2'