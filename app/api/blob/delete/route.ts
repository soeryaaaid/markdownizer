import { del } from "@vercel/blob"
import { NextResponse } from "next/server"

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = (await request.json()) as { blob_url?: string }
    if (!body.blob_url) {
      return NextResponse.json({ error: "blob_url is required" }, { status: 400 })
    }
    await del(body.blob_url)
    return NextResponse.json({ ok: true })
  } catch (error) {
    return NextResponse.json(
      { error: (error as Error).message },
      { status: 400 },
    )
  }
}