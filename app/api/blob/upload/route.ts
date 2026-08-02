import { handleUpload, type HandleUploadBody } from "@vercel/blob/client"
import { NextResponse } from "next/server"

const ALLOWED_CONTENT_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.ms-excel",
  "text/html",
  "text/plain",
  "text/csv",
  "application/json",
  "application/xml",
  "text/markdown",
  "application/epub+zip",
  "application/zip",
  "application/vnd.oasis.opendocument.text",
  "application/vnd.oasis.opendocument.presentation",
  "application/vnd.oasis.opendocument.spreadsheet",
  "application/rtf",
  "image/png",
  "image/jpeg",
  "image/gif",
  "image/bmp",
  "image/tiff",
  "image/webp",
  "audio/mpeg",
  "audio/wav",
  "audio/mp4",
  "audio/flac",
  "audio/ogg",
]

const UPLOAD_RATE_MAP = new Map<string, number[]>()
const MAX_UPLOADS_PER_MIN = 20
const UPLOAD_WINDOW_MS = 60_000
const MAX_UPLOAD_BYTES = 50 * 1024 * 1024

function clientIp(request: Request): string {
  const fwd = request.headers.get("x-forwarded-for")
  if (fwd) return fwd.split(",")[0].trim()
  return "unknown"
}

function isRateLimited(request: Request): boolean {
  const ip = clientIp(request)
  const now = Date.now()
  const hits = UPLOAD_RATE_MAP.get(ip) ?? []
  const recent = hits.filter((t) => now - t < UPLOAD_WINDOW_MS)
  if (recent.length >= MAX_UPLOADS_PER_MIN) {
    return true
  }
  recent.push(now)
  UPLOAD_RATE_MAP.set(ip, recent)
  if (UPLOAD_RATE_MAP.size > 10_000) {
    for (const [key, times] of UPLOAD_RATE_MAP) {
      if (now - times[times.length - 1] >= UPLOAD_WINDOW_MS) {
        UPLOAD_RATE_MAP.delete(key)
      }
    }
  }
  return false
}

export async function POST(request: Request): Promise<NextResponse> {
  if (isRateLimited(request)) {
    return NextResponse.json(
      { error: "Rate limit exceeded, please retry later" },
      { status: 429 },
    )
  }

  const body = (await request.json()) as HandleUploadBody

  try {
    const jsonResponse = await handleUpload({
      body,
      request,
      onBeforeGenerateToken: async () => ({
        allowedContentTypes: ALLOWED_CONTENT_TYPES,
        addRandomSuffix: true,
        maximumSizeInBytes: MAX_UPLOAD_BYTES,
      }),
      onUploadCompleted: async ({ blob }) => {
        console.log("blob upload completed", blob.url)
      },
    })

    return NextResponse.json(jsonResponse)
  } catch (error) {
    return NextResponse.json(
      { error: (error as Error).message },
      { status: 400 },
    )
  }
}
