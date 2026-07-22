import os
import tempfile
from pathlib import Path

import httpx
import trafilatura
from markitdown import MarkItDown

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
    ".html", ".htm", ".txt", ".csv", ".json", ".xml", ".md",
    ".epub", ".zip", ".odt", ".rtf",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif",
    ".webp", ".svg",
    ".mp3", ".wav", ".m4a", ".flac", ".ogg",
    ".mp4", ".webm", ".mov", ".avi", ".mkv",
}

md = MarkItDown()


def _convert_document(file_path: str) -> str:
    try:
        return md.convert(file_path).text_content
    except Exception:
        return _convert_document_fallback(file_path)


def _convert_document_fallback(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext == ".odt":
        import zipfile
        import xml.etree.ElementTree as ET

        with zipfile.ZipFile(file_path) as z:
            content = z.read("content.xml")
        root = ET.fromstring(content)
        ns = {"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
        texts = []
        for p in root.iter("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"):
            t = "".join(p.itertext())
            if t.strip():
                texts.append(t)
        return "\n\n".join(texts) if texts else f"# Document: {path.name}"
    return f"# Document: {path.name}"


def _convert_image(file_path: str) -> str:
    try:
        from PIL import Image

        img = Image.open(file_path)
        parts = [f"# Image: {Path(file_path).name}"]
        parts.append(f"- Format: {img.format}")
        parts.append(f"- Size: {img.size[0]}x{img.size[1]}")
        parts.append(f"- Mode: {img.mode}")
        info = img.info
        if info.get("description"):
            parts.append(f"- Description: {info['description']}")
        return "\n".join(parts)
    except Exception:
        size = os.path.getsize(file_path)
        parts = [f"# Image: {Path(file_path).name}"]
        parts.append(f"- File size: {size} bytes")
        return "\n".join(parts)


def _convert_audio(file_path: str) -> str:
    try:
        from tinytag import TinyTag

        tag = TinyTag.get(file_path)
        parts = [f"# Audio: {Path(file_path).name}"]
        if tag.title:
            parts.append(f"- Title: {tag.title}")
        if tag.artist:
            parts.append(f"- Artist: {tag.artist}")
        if tag.album:
            parts.append(f"- Album: {tag.album}")
        if tag.duration:
            parts.append(f"- Duration: {tag.duration:.1f}s")
        if tag.bitrate:
            parts.append(f"- Bitrate: {tag.bitrate} kbps")
        if tag.samplerate:
            parts.append(f"- Sample Rate: {tag.samplerate} Hz")
        return "\n".join(parts)
    except Exception:
        size = os.path.getsize(file_path)
        parts = [f"# Audio: {Path(file_path).name}"]
        parts.append(f"- File size: {size} bytes")
        return "\n".join(parts)


def _convert_video(file_path: str) -> str:
    try:
        from tinytag import TinyTag

        tag = TinyTag.get(file_path)
        parts = [f"# Video: {Path(file_path).name}"]
        if tag.title:
            parts.append(f"- Title: {tag.title}")
        if tag.duration:
            parts.append(f"- Duration: {tag.duration:.1f}s")
        return "\n".join(parts)
    except Exception:
        size = os.path.getsize(file_path)
        parts = [f"# Video: {Path(file_path).name}"]
        parts.append(f"- File size: {size} bytes")
        return "\n".join(parts)


ENGINES: dict[str, list] = {
    "document": [
        ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
        ".html", ".htm", ".txt", ".csv", ".json", ".xml", ".md",
        ".epub", ".zip", ".odt", ".rtf",
    ],
    "image": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif",
        ".webp", ".svg",
    ],
    "audio": [".mp3", ".wav", ".m4a", ".flac", ".ogg"],
    "video": [".mp4", ".webm", ".mov", ".avi", ".mkv"],
}


def _get_engine(ext: str) -> str | None:
    for engine, exts in ENGINES.items():
        if ext in exts:
            return engine
    return None


def convert_file(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {ext}")
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    engine = _get_engine(ext)
    if engine == "document":
        return _convert_document(file_path)
    elif engine == "image":
        return _convert_image(file_path)
    elif engine == "audio":
        return _convert_audio(file_path)
    elif engine == "video":
        return _convert_video(file_path)
    raise ValueError(f"Unknown engine for {ext}")


async def convert_url(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        result = trafilatura.extract(downloaded, output_format="markdown")
        if result:
            return result
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as f:
                f.write(content)
                tmp_path = f.name
            try:
                return _convert_document(tmp_path)
            finally:
                os.unlink(tmp_path)
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch URL: {e}")
