from cache import LRUCacheWithTTL
from fastapi import Request


def get_lru_cache(request: Request) -> LRUCacheWithTTL:
    return request.app.state.lru_cache
