import pytest
from pathlib import Path
from api.converter import convert_file, convert_url

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("filename", [
    "sample.pdf",
    "sample.docx",
    "sample.pptx",
    "sample.xlsx",
    "sample.html",
    "sample.txt",
    "sample.csv",
    "sample.json",
    "sample.xml",
    "sample.md",
    "sample.epub",
    "sample.odt",
    "sample.rtf",
])
def test_convert_document_to_markdown(filename):
    result = convert_file(str(FIXTURES_DIR / filename))
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize("filename", [
    "sample.png",
    "sample.jpg",
    "sample.webp",
    "sample.gif",
    "sample.bmp",
    "sample.tiff",
    "sample.svg",
])
def test_convert_image_to_markdown(filename):
    result = convert_file(str(FIXTURES_DIR / filename))
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize("filename", [
    "sample.mp3",
    "sample.wav",
    "sample.flac",
    "sample.m4a",
    "sample.ogg",
])
def test_convert_audio_to_markdown(filename):
    result = convert_file(str(FIXTURES_DIR / filename))
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize("filename", [
    "sample.mp4",
    "sample.webm",
    "sample.mov",
    "sample.avi",
])
def test_convert_video_to_markdown(filename):
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
