import logger
from api.api_v1 import router as v1_router
from cache import LRUCacheWithTTL
from config import Config
from fastapi import FastAPI
from middleware import LoggingMiddleware


def create_app() -> FastAPI:
    config = Config.model_validate({})

    ttl_lru_cache = LRUCacheWithTTL(config.cache_capacity)

    app = FastAPI(
        port=config.port,
        title="LRU Cache API",
        description="REST API для LRU Cache с TTL",
    )

    app.state.lru_cache = ttl_lru_cache
    app.state.config = config
    app.state.logger = logger.get_logger("APP", config.log_level, config.log_format, config.logs_path)

    # routes
    app.include_router(v1_router, prefix="/v1")

    # middlewares
    app.add_middleware(LoggingMiddleware, logger=app.state.logger)

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=app.state.config.port)
