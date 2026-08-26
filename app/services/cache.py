import json
from collections.abc import Callable
from datetime import datetime
from typing import Any

from app.core.config import settings


class TaskCache:
    def __init__(self) -> None:
        self._local: dict[str, str] = {}
        self._redis = None
        if settings.REDIS_URL:
            try:
                from redis import Redis

                self._redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._redis = None

    def get_or_set(self, key: str, factory: Callable[[], dict[str, Any]], ttl: int = 30) -> dict[str, Any]:
        cached = self._get(key)
        if cached is not None:
            return json.loads(cached)
        value = factory()
        self._set(key, json.dumps(value, default=self._json_default), ttl)
        return value

    def invalidate_owner(self, owner_id: int) -> None:
        pattern = f"tasks:{owner_id}:"
        if self._redis:
            for key in self._redis.scan_iter(f"{pattern}*"):
                self._redis.delete(key)
            return
        for key in list(self._local):
            if key.startswith(pattern):
                del self._local[key]

    def _get(self, key: str) -> str | None:
        if self._redis:
            return self._redis.get(key)
        return self._local.get(key)

    def _set(self, key: str, value: str, ttl: int) -> None:
        if self._redis:
            self._redis.setex(key, ttl, value)
            return
        self._local[key] = value

    @staticmethod
    def _json_default(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


task_cache = TaskCache()
