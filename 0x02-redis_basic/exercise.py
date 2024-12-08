#!/usr/bin/env python3
"""Storage class"""


import uuid
from functools import wraps
from typing import Union, Callable, Any
import redis


REDIS_TYPES = Union[str, bytes, memoryview]


def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        key = method.__qualname__

        self._redis.incr(key)

        return method(self, *args, **kwargs)

    return wrapper

def call_history(method: Callable) -> Callable:
    """Decorator to count how many times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        input_list = method.__qualname__ + ':inputs'
        output_list = method.__qualname__ + ':outputs'

        self._redis.rpush(input_list, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_list, str(result))
        return result

    return wrapper

def replay(method: Callable) -> None:
    """Displays the history of calls of a particular function."""
    r = redis.Redis()
    method_name = method.__qualname__
    inputs = r.lrange(f"{method_name}:inputs", 0, -1)
    outputs = r.lrange(f"{method_name}:outputs", 0, -1)

    print(f"{method_name} was called {len(inputs)} times:")
    for input, output in zip(inputs, outputs):
        print(f"{method_name}(*{input.decode('utf-8')}) -> {output.decode('utf-8')}")

class Cache:
    """Redis cache blueprint"""

    def __init__(self) -> None:
        """Instantiates the rdb and flushes the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: REDIS_TYPES) -> str:
        """Stores data in Redis and returns a unique key."""
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
        return self.get(key, lambda d: d.decode("utf-8") if isinstance(d, bytes) else d)

    def get_int(self, key: str) -> Union[int, None]:
        """Retrieves data as an integer."""
        return self.get(key, lambda d: int(d) if isinstance(d, bytes) else d)
