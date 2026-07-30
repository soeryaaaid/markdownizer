import { upload } from "@vercel/blob/client"

export async function uploadToBlob(file: File): Promise<string> {
  const blob = await upload(file.name, file, {
    access: "public",
    handleUploadUrl: "/api/blob/upload",
  })
  return blob.url
}
