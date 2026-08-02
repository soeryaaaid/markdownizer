# Markdownizer

Anything to Markdown converter. Upload a file or paste a URL and get clean Markdown back.

## Features

- **31 input formats**: Office documents, PDFs, images, audio, URLs, and more
- **Multi-engine conversion**:
  - [MarkItDown](https://github.com/microsoft/markitdown) — Office docs, HTML, EPUB, ZIP, YouTube
  - [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) — table-aware PDF extraction
  - [Gemini](https://ai.google.dev/) — image description & scanned PDF OCR fallback
  - [Groq Whisper](https://console.groq.com/) — audio transcription
  - [trafilatura](https://trafilatura.readthedocs.io/) — URL/article extraction
- **Video via browser**: no server-side ffmpeg needed — the frontend extracts audio to Opus 32k with `ffmpeg.wasm`, then transcribes the `.ogg`
- **Large files**: uploads > 4.5 MB go through [Vercel Blob](https://vercel.com/docs/storage/vercel-blob) (client upload, bypasses the request body limit)
- **API key auth**: optional, disabled when `API_KEYS` is empty

## Tech Stack

| Layer | Stack |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS 4, shadcn/ui |
| Backend | FastAPI (serverless on Vercel) |
| Deploy | Vercel — single project, dual-runtime via Services (Next.js + FastAPI) |

## Supported Formats

| Category | Formats |
|---|---|
| Documents | docx, pptx, xlsx, xls, html, htm, txt, csv, json, xml, md, epub, zip, odt, odp, ods, rtf |
| PDF | pdf |
| Images | png, jpg, jpeg, gif, bmp, tiff, tif, webp |
| Audio | mp3, wav, m4a, flac, ogg |
| URL | any article/web page, YouTube (transcript via markitdown) |

## Local Development

Prerequisites: Node.js 24, npm, Python 3.12+, [uv](https://docs.astral.sh/uv/).

```bash
# Backend dependencies
uv sync
source .venv/bin/activate

# Frontend dependencies
npm install

# Environment (export these in your shell — uvicorn doesn't read .env.local)
export API_KEYS="" GROQ_API_KEY="" GEMINI_API_KEY=""

# Run both
npm run dev            # Next.js on :3000 (calls FastAPI at :8000 directly via CORS)
uv run uvicorn api.index:app --reload --port 8000   # FastAPI
```

### Environment Variables

| Variable | Description |
|---|---|
| `API_KEYS` | Comma-separated API keys. Empty = auth disabled (public) |
| `GROQ_API_KEY` | Audio transcription (console.groq.com/keys) |
| `GEMINI_API_KEY` | Image description + scanned PDF OCR (aistudio.google.com/apikey) |
| `CORS_ORIGINS` | Comma-separated allowed origins (local dev only) |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob store token (Vercel provides automatically) |

## API

Interactive docs (Swagger UI): **`/api/docs`** — OpenAPI spec at `/api/openapi.json`.

### Authentication

If `API_KEYS` is set, every request needs a header:

```
X-API-Key: <your-api-key>
```

### Endpoints

#### `GET /api/health`

Health check. No auth required.

#### `POST /api/convert/file` — multipart upload

```
curl -X POST https://your-app.vercel.app/api/convert/file \
  -H "X-API-Key: $API_KEY" \
  -F "file=@report.pdf" \
  -F "language=en-US"
```

| Field | Type | Description |
|---|---|---|
| `file` | file | Any supported file. Direct multipart upload — max ~4.5 MB on Vercel (request body limit). For larger files, upload to Vercel Blob yourself and call `/api/convert/blob` (the web app does this automatically) |
| `language` | string | Whisper language code for audio (default `en-US`) |

#### `POST /api/convert/url` — URL/YouTube

```json
{ "url": "https://example.com/article", "language": "en-US" }
```

#### `POST /api/convert/blob` — large files

Used for files > 4.5 MB. The file must already be uploaded to [Vercel Blob](https://vercel.com/docs/storage/vercel-blob) (the web app does this client-side automatically); this endpoint just downloads it from the Blob URL and converts:

```json
{ "blob_url": "https://xxx.public.blob.vercel-storage.com/...", "filename": "report.pdf", "language": "en-US" }
```

All endpoints return:

```json
{ "markdown": "# Converted content...", "filename": "report.pdf" }
```

### Rate Limits & Limits

- `/api/convert/file` direct upload: 4.5 MB (Vercel request body limit) — larger files need `/api/convert/blob`
- Blob upload: no app-level cap (Vercel Blob platform max is 5 TB per file)
- Audio: 25 MB max (Groq Whisper upload limit)

## Deployment

Deploy to Vercel as a single project — `vercel.json` defines two services (Next.js + FastAPI) with rewrites routing `/api/*` to the Python service.

1. Push to GitHub and import the repo in Vercel
2. Set environment variables (API keys, CORS)
3. Create a Vercel Blob store — `BLOB_READ_WRITE_TOKEN` is auto-injected
4. Deploy — the Python service installs `api/requirements.txt` via uv

## Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```
