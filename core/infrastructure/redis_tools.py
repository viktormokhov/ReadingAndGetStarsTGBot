import redis.asyncio as redis

class RedisClient:
    def __init__(self, url: str):
        self._url = url
        self._redis = None

    async def connect(self):
        if not self._redis:
            self._redis = await redis.from_url(self._url, decode_responses=False)  # decode_responses=False чтобы хранить байты
        return self._redis

    async def set(self, key, value, ex=None):
        r = await self.connect()
        await r.set(key, value, ex=ex)

    async def get(self, key):
        r = await self.connect()
        return await r.get(key)

    async def delete(self, key):
        r = await self.connect()
        await r.delete(key)

    async def incr(self, key):
        r = await self.connect()
        return await r.incr(key)

    async def get_int(self, key, default=0):
        r = await self.connect()
        value = await r.get(key)
        if value is None:
            return default
        # If stored as bytes, decode to string first
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    async def count_keys(self, pattern):
        """
        Count the number of keys matching the given pattern.
        Uses SCAN for better performance on large databases.
        """
        r = await self.connect()
        count = 0
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=pattern, count=100)
            count += len(keys)
            if cursor == 0:
                break
        return count
