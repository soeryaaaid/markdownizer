import mimetypes
import os
import tempfile
from pathlib import Path


def convert_image(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "# Image description failed. Please try again later."
    try:
        _, mime = mimetypes.guess_type(file_path)
        mime = mime or "image/jpeg"
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        data: bytes | None = None
        if ext in (".bmp", ".tiff", ".tif"):
            from PIL import Image

            img = Image.open(file_path)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp, format="PNG")
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                data = f.read()
            os.unlink(tmp_path)
            mime = "image/png"
        else:
            with open(file_path, "rb") as f:
                data = f.read()
        if data is None:
            return "# Image description failed. Please try again later."
        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=data, mime_type=mime),
                        types.Part.from_text(text="Describe this image in Markdown format."),
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL),
            ),
        )
        if response.text and response.text.strip():
            return response.text.strip()
    except Exception:
        pass
    return "# Image description failed. Please try again later."
