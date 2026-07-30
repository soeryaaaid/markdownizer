import json
import re
from pathlib import Path

from striprtf.striprtf import rtf_to_text

from api.converters.opendoc import convert_opendoc


def _convert_rtf(file_path: str) -> str | None:
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        text = rtf_to_text(raw)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text if text else None
    except Exception:
        return None


def _convert_xml(file_path: str) -> str | None:
    try:
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
        return f"```xml\n{raw}\n```"
    except Exception:
        return None


def _convert_json(file_path: str) -> str | None:
    try:
        with open(file_path, encoding="utf-8") as f:
            parsed = json.load(f)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        return f"```json\n{formatted}\n```"
    except Exception:
        return None


def _convert_txt(file_path: str) -> str | None:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        text = text.strip()
        return text if text else None
    except Exception:
        return None


def _try_markitdown(file_path: str) -> str | None:
    try:
        from api.converter import get_base_md

        md = get_base_md().convert(file_path).markdown
        return md.strip() or None
    except Exception:
        return None


def convert_document(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    raw_formats = (".rtf", ".xml", ".json")

    if ext not in raw_formats:
        result = _try_markitdown(file_path)
        if result:
            return result

    converters: list[tuple[tuple[str, ...], callable]] = [
        ((".odt", ".odp", ".ods"), convert_opendoc),
        ((".rtf",), _convert_rtf),
        ((".xml",), _convert_xml),
        ((".json",), _convert_json),
        ((".txt",), _convert_txt),
    ]
    for exts, fn in converters:
        if ext in exts:
            result = fn(file_path)
            if result:
                return result

    result = _try_markitdown(file_path)
    if result:
        return result

    return (
        f"# Document `{Path(file_path).name}` conversion failed."
        " The format may be unsupported or the file may be corrupted."
    )
