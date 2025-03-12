from unittest.mock import patch

import pytest

from app.cache import CacheOperationResult, LRUCacheWithTTL


@pytest.fixture(scope="function")
def cache() -> LRUCacheWithTTL:
    return LRUCacheWithTTL(3)


def test_cache_initialization():
    cache = LRUCacheWithTTL(3)
    assert cache.capacity == 3


def test_cache_initialization_with_negative_capacity():
    with pytest.raises(ValueError):
        LRUCacheWithTTL(-1)


def test_put_and_get(cache: LRUCacheWithTTL):
    assert cache.put("a", 1) == CacheOperationResult.CREATED
    assert cache.stats.size == 1
    assert cache.get("a") == (1, CacheOperationResult.HIT)


def test_update_existing_key(cache: LRUCacheWithTTL):
    cache.put("a", 1)
    assert cache.put("a", 2) == CacheOperationResult.UPDATED
    assert cache.get("a") == (2, CacheOperationResult.HIT)


def test_update_existing_key_move_to_end(cache: LRUCacheWithTTL):
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.put("a", 4)

    assert cache.get("a") == (4, CacheOperationResult.HIT)
    assert cache.stats.items == ("a", "c", "b")


def test_update_existing_key_saves_size(cache: LRUCacheWithTTL):
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.put("a", 4)

    assert cache.stats.size == 3

def test_get_missing_key(cache: LRUCacheWithTTL):
    assert cache.get("missing") == (None, CacheOperationResult.MISS)


def test_cache_eviction(cache: LRUCacheWithTTL):
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.put("d", 4)

    assert cache.stats.size == 3
    assert cache.get("a") == (None, CacheOperationResult.MISS)
    assert cache.get("b") == (2, CacheOperationResult.HIT)
    assert cache.get("d") == (4, CacheOperationResult.HIT)


def test_lru(cache: LRUCacheWithTTL):
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)

    assert cache.get("a") == (1, CacheOperationResult.HIT)
    assert cache.get("b") == (2, CacheOperationResult.HIT)
    assert cache.get("c") == (3, CacheOperationResult.HIT)

    assert cache.stats.items == ("c", "b", "a")


def test_ttl_expiry(cache: LRUCacheWithTTL):
    with patch("app.cache.time.time", return_value=100):
        cache.put("a", 1, ttl=10)

    with patch("app.cache.time.time", return_value=110):
        assert cache.get("a") == (1, CacheOperationResult.HIT)

    with patch("app.cache.time.time", return_value=111):
        assert cache.get("a") == (None, CacheOperationResult.EXPIRED)

    assert cache.get("a") == (None, CacheOperationResult.MISS)


def test_delete_key(cache: LRUCacheWithTTL):
    cache.put("a", 1)
    assert cache.delete("a") == CacheOperationResult.DELETED
    assert cache.stats.size == 0
    assert cache.get("a") == (None, CacheOperationResult.MISS)


def test_delete_missing_key(cache: LRUCacheWithTTL):
    assert cache.delete("missing") == CacheOperationResult.MISS


def test_capacity_property(cache: LRUCacheWithTTL):
    assert cache.capacity == 3


def test_cache_stats(cache: LRUCacheWithTTL):
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)

    stats = cache.stats
    assert stats.size == 3
    assert stats.capacity == 3
    assert stats.items == ("c", "b", "a")
