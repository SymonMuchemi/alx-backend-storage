#!/usr/bin/env python3
"""Storage class"""


import uuid
from typing import Union
from redis import Redis


class Cache:
    """Redis cache blueprint"""

    def __init__(self) -> None:
        """Instantiates the rdb and flushes the database."""
        self._redis = Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores data in Redis and returns the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)

        return key
