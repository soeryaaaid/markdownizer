import json
import os
import subprocess


def get_media_duration(file_path: str) -> float | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except Exception:
        return None


MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB Groq upload limit


def convert_audio(file_path: str, language: str = "en-US") -> str:
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        return "# Audio too large (max 25 MB)."
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "# Audio transcription failed. Please try again later."
    result = _transcribe_with_groq(file_path, api_key, language)
    return result if result else "# Audio transcription failed. Please try again later."


def _transcribe_with_groq(file_path: str, api_key: str, language: str) -> str | None:
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    lang_code = language.split("-")[0] if language else None
    kwargs = {}
    if lang_code and len(lang_code) == 2:
        kwargs["language"] = lang_code

    with open(file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=f,
            response_format="text",
            **kwargs,
        )
    return transcript.strip() if transcript else None
