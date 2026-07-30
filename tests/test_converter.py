from pathlib import Path

import pytest

from api.converter import convert_file, convert_url

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    "filename",
    [
        "sample.pdf",
        "sample.docx",
        "sample.doc",
        "sample.pptx",
        "sample.ppt",
        "sample.xlsx",
        "sample.xls",
        "sample.html",
        "sample.htm",
        "sample.txt",
        "sample.csv",
        "sample.json",
        "sample.xml",
        "sample.md",
        "sample.epub",
        "sample.odt",
        "sample.odp",
        "sample.ods",
        "sample.rtf",
        "sample.zip",
    ],
)
def test_convert_document_to_markdown(filename):
    result = convert_file(str(FIXTURES_DIR / filename))
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize(
    "filename",
    [
        "sample.png",
        "sample.jpg",
        "sample.jpeg",
        "sample.webp",
        "sample.gif",
        "sample.bmp",
        "sample.tiff",
        "sample.tif",
    ],
)
def test_convert_image_to_markdown(filename):
    result = convert_file(str(FIXTURES_DIR / filename))
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize(
    "filename",
    [
        "sample.mp3",
        "sample.wav",
        "sample.flac",
        "sample.m4a",
        "sample.ogg",
    ],
)
def test_convert_audio_to_markdown(filename):
    result = convert_file(str(FIXTURES_DIR / filename))
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_convert_url_to_markdown():
    result = await convert_url("https://example.com")
    assert isinstance(result, str)
    assert len(result) > 0


def test_convert_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        convert_file("nonexistent.pdf")


def test_convert_unsupported_format():
    with pytest.raises(ValueError):
        convert_file("unsupported.xyz")


def test_auth_valid_api_key():
    from api.auth import verify_api_key

    assert verify_api_key("valid-test-key-12345") is True
    assert verify_api_key("") is False
    assert verify_api_key(None) is False
