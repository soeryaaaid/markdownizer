import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.index import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_convert_url_endpoint_no_auth(client):
    response = await client.post(
        "/api/convert/url",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_convert_url_endpoint_with_valid_auth(client):
    response = await client.post(
        "/api/convert/url",
        json={"url": "https://example.com"},
        headers={"X-API-Key": "valid-test-key-12345"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "markdown" in data
    assert len(data["markdown"]) > 0


@pytest.mark.asyncio
async def test_convert_url_endpoint_with_invalid_auth(client):
    response = await client.post(
        "/api/convert/url",
        json={"url": "https://example.com"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_convert_url_endpoint_empty_url(client):
    response = await client.post(
        "/api/convert/url",
        json={"url": ""},
        headers={"X-API-Key": "valid-test-key-12345"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_convert_file_endpoint_no_file(client):
    response = await client.post(
        "/api/convert/file",
        headers={"X-API-Key": "valid-test-key-12345"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_openapi_docs_available(client):
    response = await client.get("/api/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_openapi_schema(client):
    response = await client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/convert/url" in schema["paths"]
    assert "/api/convert/file" in schema["paths"]
