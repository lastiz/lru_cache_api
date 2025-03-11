from http import HTTPStatus

from cache import CacheOperationResult
from fastapi.responses import JSONResponse, Response

OP_RESULT_TO_HTTP_CODE = {
    CacheOperationResult.HIT: HTTPStatus.OK,
    CacheOperationResult.CREATED: HTTPStatus.CREATED,
    CacheOperationResult.UPDATED: HTTPStatus.OK,
    CacheOperationResult.DELETED: HTTPStatus.NO_CONTENT,
    CacheOperationResult.MISS: HTTPStatus.NOT_FOUND,
    CacheOperationResult.EXPIRED: HTTPStatus.NOT_FOUND,
}


OP_RESULT_TO_MSG = {
    CacheOperationResult.HIT: "OK",
    CacheOperationResult.CREATED: "Cache item created",
    CacheOperationResult.UPDATED: "Cache item updated",
    CacheOperationResult.DELETED: "Cache item deleted",
    CacheOperationResult.MISS: "Cache item not found",
    CacheOperationResult.EXPIRED: "Cache item expired",
}


def make_response(op_result: CacheOperationResult, content: dict | None = None) -> JSONResponse | Response:
    if op_result.is_negative():
        content = {"message": OP_RESULT_TO_MSG[op_result]}

    if content is None:
        return Response(status_code=OP_RESULT_TO_HTTP_CODE[op_result])

    return JSONResponse(content=content, status_code=OP_RESULT_TO_HTTP_CODE[op_result])
