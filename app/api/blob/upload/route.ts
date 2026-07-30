import { handleUpload, type HandleUploadBody } from "@vercel/blob/client"
import { NextResponse } from "next/server"

const ALLOWED_CONTENT_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/msword",
  "application/vnd.ms-powerpoint",
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
  "image/svg+xml",
  "audio/mpeg",
  "audio/wav",
  "audio/mp4",
  "audio/flac",
  "audio/ogg",
]

export async function POST(request: Request): Promise<NextResponse> {
  const body = (await request.json()) as HandleUploadBody

  try {
    const jsonResponse = await handleUpload({
      body,
      request,
      onBeforeGenerateToken: async () => ({
        allowedContentTypes: ALLOWED_CONTENT_TYPES,
        addRandomSuffix: true,
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
