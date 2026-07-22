import os
import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from api.auth import require_api_key
from api.converter import convert_file, convert_url

app = FastAPI(
    title="Markdownizer API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


class ConvertURLRequest(BaseModel):
    url: str


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
    if not body.url.strip():
        raise HTTPException(status_code=422, detail="URL cannot be empty")
    markdown = await convert_url(body.url)
    return ConvertResponse(markdown=markdown)


@app.post("/api/convert/file", response_model=ConvertResponse)
async def convert_file_endpoint(
    file: UploadFile = File(...),
    api_key: str = Depends(require_api_key),
):
    if not file.filename:
        raise HTTPException(status_code=422, detail="No file provided")
    suffix = Path(file.filename).suffix or ".tmp"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        markdown = convert_file(tmp_path)
        return ConvertResponse(markdown=markdown, filename=file.filename)
    finally:
        os.unlink(tmp_path)
