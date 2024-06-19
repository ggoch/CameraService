import redis

REDIS_URL = "redis://localhost:6379"

def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)

    value = 'bar'
    redis_connection.set('foo', value )
    result = redis_connection.get('foo')
    redis_connection.close()

    assert result.decode() == value

connection_pool = redis.ConnectionPool.from_url(REDIS_URL)

def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=connection_pool)

    value = 'bar2'
    redis_connection.set('foo2', value )
    result = redis_connection.get('foo2')
    redis_connection.close()

    assert result.decode() == value