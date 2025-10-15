import asyncio
import uuid
import logging
from app.settings import settings


# Redis Lock class
class RedisLock:
    """
    قفل توزیع‌شده با استفاده از Redis و الگوریتم SET NX PX
    شامل:
      - TTL ثابت (۵ ثانیه)
      - تمدید خودکار (auto-renewal)
      - آزادسازی امن با Lua script
    """

    LUA_RELEASE_SCRIPT = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """

    def __init__(self, redis, key: str):
        self.redis = redis
        self.key = key
        self.ttl = settings.lock_ttl
        self.value = str(uuid.uuid4())
        self._renew_task = None
        self._logger = logging.getLogger("RedisLock")

    async def acquire(self) -> bool:
        """دریافت قفل با SET NX PX"""
        result = await self.redis.set(self.key, self.value, px=self.ttl, nx=True)
        if result:
            self._logger.debug(f"Lock acquired for {self.key}")
            self._renew_task = asyncio.create_task(self._auto_renew())
            return True
        self._logger.debug(f"Lock already held for {self.key}")
        return False

    async def release(self):
        """آزادسازی امن قفل با Lua script"""
        if self._renew_task:
            self._renew_task.cancel()
        try:
            await self.redis.eval(self.LUA_RELEASE_SCRIPT, 1, self.key, self.value)
            self._logger.debug(f"Lock released for {self.key}")
        except Exception as e:
            self._logger.error(f"Failed to release lock {self.key}: {e}")

    async def _auto_renew(self):
        """تمدید خودکار TTL تا زمان در اختیار بودن قفل"""
        try:
            while True:
                await asyncio.sleep(self.ttl / 3000)  # تمدید در 2/3 مدت TTL
                await self.redis.pexpire(self.key, self.ttl)
        except asyncio.CancelledError:
            pass
