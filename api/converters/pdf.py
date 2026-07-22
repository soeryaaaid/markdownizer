import os


def convert_pdf(file_path: str) -> str:
    try:
        import pymupdf4llm

        result = pymupdf4llm.to_markdown(file_path)
        if result.strip():
            return result.strip()
    except Exception:
        pass

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            result = _convert_pdf_with_gemini(file_path, api_key)
            if result:
                return result
        except Exception:
            pass

    from api.converter import get_base_md

    try:
        return get_base_md().convert(file_path).markdown
    except Exception:
        pass
    return (
        "# PDF could not be converted."
        " The file may contain only scanned images with no extractable text."
    )


def _convert_pdf_with_gemini(file_path: str, api_key: str) -> str | None:
    from google import genai

    client = genai.Client(api_key=api_key)

    pdf_file = client.files.upload(file=file_path)
    while pdf_file.state == "PROCESSING":
        pdf_file = client.files.get(name=pdf_file.name)
    if pdf_file.state == "FAILED":
        return None

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            genai.types.Content(
                role="user",
                parts=[
                    genai.types.Part.from_uri(
                        file_uri=pdf_file.uri,
                        mime_type=pdf_file.mime_type or "application/pdf",
                    ),
                    genai.types.Part.from_text(
                        text=(
                            "Convert this document to Markdown. "
                            "Preserve headings, paragraphs, lists, tables, "
                            "code blocks, and formatting. "
                            "For any figures, charts, diagrams, or images "
                            "that cannot be represented in Markdown, "
                            "describe them in detail within square brackets, "
                            "e.g., [Figure: ...]."
                        ),
                    ),
                ],
            ),
        ],
    )
    return response.text if response.text else None
