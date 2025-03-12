import enum
import threading
import time
import typing as t
from collections import OrderedDict


class CachedItem(t.NamedTuple):
    item: t.Any
    saved_at: float
    ttl: int | None = None


class CacheStats(t.NamedTuple):
    size: int
    capacity: int
    items: tuple


class CacheOperationResult(enum.IntEnum):
    # positive
    HIT = 0
    CREATED = 1
    UPDATED = 2
    DELETED = 3

    # negative
    MISS = 100
    EXPIRED = 101

    def is_negative(self) -> bool:
        return self.value >= 100


class LRUCacheWithTTL:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")

        self._capacity = capacity
        self._cache: OrderedDict[t.Hashable, CachedItem] = OrderedDict()

        # asyncio safety методы кеша синхронные
        # thread safety, если доступ к кешу из другого потока
        self._cache_thread_lock = threading.Lock()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def stats(self) -> CacheStats:
        with self._cache_thread_lock:
            return CacheStats(len(self._cache), self._capacity, tuple(reversed(self._cache.keys())))

    def get(self, key: t.Hashable) -> tuple[t.Any, CacheOperationResult]:
        with self._cache_thread_lock:
            if not key in self._cache:
                return None, CacheOperationResult.MISS

            cached_item = self._cache[key]
            if not cached_item.ttl is None and time.time() > cached_item.saved_at + cached_item.ttl:
                del self._cache[key]
                return None, CacheOperationResult.EXPIRED

            self._cache.move_to_end(key)
            return cached_item.item, CacheOperationResult.HIT

    def put(self, key: t.Hashable, val: t.Any, ttl: int | None = None) -> CacheOperationResult:
        if not ttl is None and ttl <= 0:
            raise ValueError("TTL must be greater than 0")

        with self._cache_thread_lock:
            operation_result = CacheOperationResult.CREATED

            if key in self._cache:
                operation_result = CacheOperationResult.UPDATED

            if len(self._cache) >= self._capacity and operation_result == CacheOperationResult.CREATED:
                self._cache.popitem(last=False)

            saved_at = time.time()
            self._cache[key] = CachedItem(val, saved_at, ttl)
            return operation_result

    def delete(self, key: t.Hashable) -> CacheOperationResult:
        with self._cache_thread_lock:
            cached_item = self._cache.pop(key, None)

            if cached_item is None:
                return CacheOperationResult.MISS

            return CacheOperationResult.DELETED
