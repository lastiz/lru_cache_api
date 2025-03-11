from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Config
from app.main import create_app

mock_logger = MagicMock()


mock_config = Config.model_validate(
    {
        "cache_capacity": 3,
        "port": 8000,
        "log_level": "DEBUG",
        "log_format": "%(name)s | %(asctime)s | %(levelname)s | %(message)s",
    }
)


@pytest.fixture(scope="module")
def application():
    with patch("config.Config.model_validate", return_value=mock_config):
        with patch("logger.get_logger", return_value=mock_logger):
            yield create_app()


@pytest.fixture(scope="module")
def client(application: FastAPI):
    with TestClient(application, base_url="http://localhost/v1") as test_client:
        yield test_client


@pytest.fixture
def clear_cache(client: TestClient):
    client.delete("/cache/key1")
    client.delete("/cache/key2")
    client.delete("/cache/key3")
    client.delete("/cache/key4")


def test_get_empty_stats(clear_cache, client: TestClient):
    response = client.get("/cache/stats")
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body["size"] == 0
    assert body["capacity"] == 3
    assert body["items"] == []


def test_put_and_get(clear_cache, client: TestClient):
    response = client.put("/cache/key1", json={"value": "test_value", "ttl": 30})
    assert response.status_code == HTTPStatus.CREATED

    response = client.get("/cache/key1")
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body == {"value": "test_value"}


def test_update_existing_item(clear_cache, client: TestClient):
    client.put("/cache/key1", json={"value": "test_value", "ttl": 30})
    response = client.put("/cache/key1", json={"value": "test_value2", "ttl": 30})
    assert response.status_code == HTTPStatus.OK

    response = client.get("/cache/key1")
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body == {"value": "test_value2"}


def test_get_missing_item(clear_cache, client: TestClient):
    response = client.get("/cache/missing_key")
    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()
    assert body["message"] == "Cache item not found"


def test_cache_eviction(clear_cache, client: TestClient):
    client.put("/cache/key1", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key2", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key3", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key4", json={"value": "test_value", "ttl": 30})

    response = client.get("/cache/key1")
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = client.get("/cache/key2")
    assert response.status_code == HTTPStatus.OK

    response = client.get("/cache/key4")
    assert response.status_code == HTTPStatus.OK


def test_get_expired_item(clear_cache, client: TestClient):
    with patch("app.cache.time.time", return_value=100):
        client.put("/cache/key1", json={"value": "test_value", "ttl": 10})

    with patch("app.cache.time.time", return_value=111):
        response = client.get("/cache/key1")

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()
    assert body["message"] == "Cache item expired"


def test_lru(clear_cache, client: TestClient):
    client.put("/cache/key1", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key2", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key3", json={"value": "test_value", "ttl": 30})

    response = client.get("/cache/key1")
    assert response.status_code == HTTPStatus.OK

    response = client.get("/cache/key2")
    assert response.status_code == HTTPStatus.OK

    response = client.get("/cache/key3")
    assert response.status_code == HTTPStatus.OK

    response = client.get("/cache/stats")
    body = response.json()

    assert body["items"] == ["key3", "key2", "key1"]


def test_delete_item(clear_cache, client: TestClient):
    client.put("/cache/key1", json={"value": "test_value", "ttl": 30})
    response = client.delete("/cache/key1")
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get("/cache/key1")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_missing_item(clear_cache, client: TestClient):
    response = client.delete("/cache/missing_key")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_cache_stats(clear_cache, client: TestClient):
    client.put("/cache/key1", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key2", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key3", json={"value": "test_value", "ttl": 30})
    client.put("/cache/key4", json={"value": "test_value", "ttl": 30})

    response = client.get("/cache/stats")
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body["size"] == 3
    assert body["capacity"] == 3
    assert body["items"] == ["key4", "key3", "key2"]


def test_validate_ttl(clear_cache, client: TestClient):
    response = client.put("/cache/key1", json={"value": "test_value", "ttl": -1})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT

    response = client.get("/cache/key1")
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = client.put("/cache/key1", json={"value": "test_value", "ttl": 0})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT

    response = client.get("/cache/key1")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_logging_middleware():
    mock_logger.info.assert_called()
