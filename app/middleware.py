import time
import typing as t

from fastapi.requests import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class LoggerProtocol(t.Protocol):
    def debug(self, msg: str) -> None: ...
    def info(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...
    def critical(self, msg: str) -> None: ...


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, logger: LoggerProtocol) -> None:
        self.logger = logger
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: t.Callable[..., t.Awaitable[Response]]) -> Response:
        now = time.time()

        try:
            response = await call_next(request)

        finally:
            duration = time.time() - now
            self.logger.info(f"Request {request.method} {request.url.path}. Took {duration:.5f}s")

        return response
