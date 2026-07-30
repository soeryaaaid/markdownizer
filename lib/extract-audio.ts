import { FFmpeg } from "@ffmpeg/ffmpeg"
import { fetchFile } from "@ffmpeg/util"

let ffmpeg: FFmpeg | null = null
let loading: Promise<void> | null = null

const VIDEO_EXTS = new Set([".mp4", ".webm", ".mov", ".avi", ".mkv"])

function getExt(name: string) {
  const i = name.lastIndexOf(".")
  return i >= 0 ? name.slice(i).toLowerCase() : ""
}

export function isVideo(name: string) {
  return VIDEO_EXTS.has(getExt(name))
}

export function getVideoDuration(file: File): Promise<number> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const video = document.createElement("video")
    video.preload = "metadata"
    video.onloadedmetadata = () => {
      URL.revokeObjectURL(url)
      resolve(video.duration)
    }
    video.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error("Failed to load video metadata"))
    }
    video.src = url
  })
}

export function preloadFfmpeg() {
  if (!ffmpeg && !loading) {
    ffmpeg = new FFmpeg()
    loading = ffmpeg.load().then(() => { loading = null })
  }
  return loading
}

export async function extractAudio(file: File) {
  if (loading) await loading
  if (!ffmpeg) {
    ffmpeg = new FFmpeg()
    await ffmpeg.load()
  }

  const inputName = `input${getExt(file.name)}`

  await ffmpeg.writeFile(inputName, await fetchFile(file))
  await ffmpeg.exec([
    "-i", inputName,
    "-vn", "-c:a", "libopus",
    "-b:a", "32k",
    "-ar", "16000", "-ac", "1",
    "-y", "output.ogg",
  ])
  const raw = await ffmpeg.readFile("output.ogg")

  await ffmpeg.deleteFile(inputName)
  await ffmpeg.deleteFile("output.ogg")

  return new Blob([raw as unknown as BlobPart], { type: "audio/ogg" })
}
