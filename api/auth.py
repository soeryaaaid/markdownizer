import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _get_valid_keys() -> list[str]:
    raw = os.environ.get("API_KEYS", "")
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k.strip()]


def verify_api_key(api_key: str | None) -> bool:
    if not api_key:
        return False
    valid_keys = _get_valid_keys()
    if not valid_keys:
        return False
    return api_key in valid_keys


async def require_api_key(api_key: str | None = Security(api_key_header)):
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key
