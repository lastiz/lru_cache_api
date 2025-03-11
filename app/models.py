import typing as t

from pydantic import BaseModel, Field


class ItemValueSchema(BaseModel):
    value: t.Any


class PutCacheItemSchema(BaseModel):
    value: t.Any
    ttl: int | None = Field(default=None, gt=0)


class CacheStatsResponseSchema(BaseModel):
    size: int
    capacity: int
    items: tuple


class ErrorResponseSchema(BaseModel):
    message: str
