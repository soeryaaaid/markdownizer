import asyncio
import os
import re
import tempfile
from pathlib import Path

import httpx
import trafilatura
from markitdown import MarkItDown

from api.converters.audio import convert_audio
from api.converters.document import convert_document
from api.converters.image import convert_image
from api.converters.pdf import convert_pdf

ENGINES: dict[str, frozenset[str]] = {
    "document": frozenset(
        {
            ".docx",
            ".doc",
            ".pptx",
            ".ppt",
            ".xlsx",
            ".xls",
            ".html",
            ".htm",
            ".txt",
            ".csv",
            ".json",
            ".xml",
            ".md",
            ".epub",
            ".zip",
            ".odt",
            ".odp",
            ".ods",
            ".rtf",
        }
    ),
    "pdf": frozenset({".pdf"}),
    "image": frozenset(
        {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".tif",
            ".webp",
        }
    ),
    "audio": frozenset({".mp3", ".wav", ".m4a", ".flac", ".ogg"}),
}

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset().union(*ENGINES.values())

_md_base: MarkItDown | None = None


def get_base_md() -> MarkItDown:
    global _md_base
    if _md_base is None:
        _md_base = MarkItDown()
    return _md_base


_HANDLERS: dict[str, callable] = {
    "document": convert_document,
    "pdf": convert_pdf,
    "image": convert_image,
    "audio": convert_audio,
}


def _get_engine(ext: str) -> str | None:
    for engine, exts in ENGINES.items():
        if ext in exts:
            return engine
    return None


def _normalize_youtube_url(url: str) -> str | None:
    patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([\w-]{11})",
        r"(?:https?://)?youtu\.be/([\w-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([\w-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/live/([\w-]{11})",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            vid = m.group(1)
            return f"https://www.youtube.com/watch?v={vid}"
    return None


def convert_file(file_path: str, language: str = "en-US") -> str:
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {ext}")
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    engine = _get_engine(ext)
    handler = _HANDLERS[engine]
    kw: dict = {}
    if engine == "audio":
        kw["language"] = language
    return handler(file_path, **kw)


async def convert_url(url: str, language: str = "en-US") -> str:
    yt_url = _normalize_youtube_url(url)
    if yt_url:
        url = yt_url

    try:
        result = get_base_md().convert(url).markdown
        if result.strip():
            return result.strip()
    except Exception:
        pass

    downloaded = await asyncio.to_thread(trafilatura.fetch_url, url)
    if downloaded:
        result = trafilatura.extract(downloaded, output_format="markdown")
        if result:
            return result
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(response.text)
            tmp_path = f.name
        try:
            return convert_document(tmp_path)
        finally:
            os.unlink(tmp_path)
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch URL: {e}")
