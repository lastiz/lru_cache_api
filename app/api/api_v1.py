import typing as t
from http import HTTPStatus

from cache import CacheStats, LRUCacheWithTTL
from dependencies import get_lru_cache
from fastapi import APIRouter, Depends
from models import (
    CacheStatsResponseSchema,
    ErrorResponseSchema,
    ItemValueSchema,
    PutCacheItemSchema,
)
from utils import make_response

router = APIRouter(
    prefix="/cache",
    tags=["API v1"],
)


@router.get(
    "/stats",
    response_model=CacheStatsResponseSchema,
    description="Get cache statistics",
)
async def get_stats(lru_cache: t.Annotated[LRUCacheWithTTL, Depends(get_lru_cache)]) -> CacheStats:
    return lru_cache.stats


@router.get(
    "/{key}",
    response_model=ItemValueSchema,
    responses={
        HTTPStatus.NOT_FOUND: {"model": ErrorResponseSchema, "description": "Cache item not found or expired"}
    },
    description="Get cache item by key",
)
async def get_item(key: str, lru_cache: t.Annotated[LRUCacheWithTTL, Depends(get_lru_cache)]):
    item, op_result = lru_cache.get(key)
    return make_response(op_result, {"value": item})


@router.put(
    "/{key}",
    status_code=HTTPStatus.CREATED,
    responses={HTTPStatus.OK: {"description": "Cache item updated"}},
    description="Put cache item by key",
)
async def put_item(
    key: str, item_schema: PutCacheItemSchema, lru_cache: t.Annotated[LRUCacheWithTTL, Depends(get_lru_cache)]
):
    op_result = lru_cache.put(key, item_schema.value, item_schema.ttl)
    return make_response(op_result)


@router.delete(
    "/{key}",
    status_code=HTTPStatus.NO_CONTENT,
    responses={HTTPStatus.NOT_FOUND: {"model": ErrorResponseSchema, "description": "Cache item not found"}},
    description="Delete cache item by key",
)
async def delete_item(key: str, lru_cache: t.Annotated[LRUCacheWithTTL, Depends(get_lru_cache)]):
    op_result = lru_cache.delete(key)
    return make_response(op_result)
