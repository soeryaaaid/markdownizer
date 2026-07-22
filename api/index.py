import os
import tempfile
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from api.auth import require_api_key
from api.converter import convert_file, convert_url

app = FastAPI(
    title="Markdownizer API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConvertURLRequest(BaseModel):
    url: str
    language: str = "en-US"

    @field_validator("url")
    @classmethod
    def url_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("URL cannot be empty")
        return v


class ConvertBlobRequest(BaseModel):
    blob_url: str
    filename: str | None = None
    language: str = "en-US"

    @field_validator("blob_url")
    @classmethod
    def url_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("blob_url cannot be empty")
        return v


class ConvertResponse(BaseModel):
    markdown: str
    filename: str | None = None


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/convert/url", response_model=ConvertResponse)
async def convert_url_endpoint(
    body: ConvertURLRequest,
    api_key: str = Depends(require_api_key),
):
    markdown = await convert_url(body.url)
    return ConvertResponse(markdown=markdown)


@app.post("/api/convert/file", response_model=ConvertResponse)
async def convert_file_endpoint(
    file: UploadFile = File(...),
    language: str = Form("en-US"),
    api_key: str = Depends(require_api_key),
):
    if not file.filename:
        raise HTTPException(status_code=422, detail="No file provided")
    suffix = Path(file.filename).suffix or ".tmp"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        markdown = convert_file(
            tmp_path,
            language=language,
        )
        return ConvertResponse(markdown=markdown, filename=file.filename)
    finally:
        os.unlink(tmp_path)


@app.post("/api/convert/blob", response_model=ConvertResponse)
async def convert_blob_endpoint(
    body: ConvertBlobRequest,
    api_key: str = Depends(require_api_key),
):
    filename = body.filename or body.blob_url.rstrip("/").split("/")[-1]
    ext = Path(filename).suffix or ".tmp"

    async with httpx.AsyncClient() as client:
        resp = await client.get(body.blob_url)
        resp.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(resp.content)
        tmp_path = tmp.name
    try:
        markdown = convert_file(tmp_path, language=body.language)
        return ConvertResponse(markdown=markdown, filename=filename)
    finally:
        os.unlink(tmp_path)
