#!/usr/bin/env python3
"""Storage class"""


import uuid
from typing import Union, Callable, Any
import redis


REDIS_TYPES = Union[str, bytes, memoryview]


class Cache:
    """Redis cache blueprint"""

    def __init__(self) -> None:
        """Instantiates the rdb and flushes the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[REDIS_TYPES]) -> str:
        """Stores data in Redis and returns the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)

        return key

    def get(self, key: str, fn: Callable[[REDIS_TYPES], Any] = None) -> Any:
        """Retrieves data from Redis and applies
        an optional conversion function."""
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """Retrieves data as a string."""
        return self.get(
            key,
            lambda d: d.decode('utf-8') if isinstance(d, bytes) else d)

    def get_int(self, key: str) -> Union[int, None]:
        """Retrieves data as an integer."""
        return self.get(key, lambda d: int(d) if isinstance(d, bytes) else d)
