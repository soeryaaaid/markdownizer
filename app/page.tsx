"use client"

import { useState, useCallback } from "react"
import { ArrowRight, Copy, Check, Settings } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { HugeiconsIcon } from "@hugeicons/react"
import { File01Icon, LinkSquare02Icon } from "@hugeicons/core-free-icons"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { FileUpload } from "@/components/ui/file-upload"
import { UrlInput } from "@/components/UrlInput"
import { CollapsibleSidebar, CollapsibleSidebarHeader, CollapsibleSidebarBody } from "@/components/ui/collapsible-sidebar"
import { SettingsPanel } from "@/components/settings-panel"
import { Header } from "@/components/Header"
import { Toaster, toast } from "sonner"
import { isVideo, extractAudio, preloadFfmpeg, getVideoDuration } from "@/lib/extract-audio"
import { uploadToBlob } from "@/lib/blob-upload"
import { loadSettings, saveSettings, type AppSettings } from "@/lib/settings"
import { useEffect } from "react"

type Mode = "file" | "url"
type View = "raw" | "preview"

const API =
  typeof location < "u" && location.hostname === "localhost"
    ? "http://localhost:8000"
    : ""

const MAX_DIRECT_UPLOAD = 4.5 * 1024 * 1024

export default function Page() {
  const [mode, setMode] = useState<Mode>("file")
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState("")
  const [result, setResult] = useState("")
  const [view, setView] = useState<View>("raw")
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [settings, setSettings] = useState<AppSettings>(loadSettings)
  const [videoError, setVideoError] = useState<string | null>(null)

  useEffect(() => {
    if (file && isVideo(file.name)) {
      preloadFfmpeg()
      getVideoDuration(file).then(d => {
        if (d > 1800) setVideoError(`Video too long (${(d / 60).toFixed(0)} min). Max 30 min.`)
        else setVideoError(null)
      })
    } else {
      setVideoError(null)
    }
  }, [file])

  const updateSettings = useCallback((s: AppSettings) => {
    setSettings(s)
    saveSettings(s)
  }, [])

  function isValidUrl(s: string) {
    try {
      const u = new URL(s.startsWith("http") ? s : `https://${s}`)
      if (u.protocol !== "http:" && u.protocol !== "https:") return false
      return u.hostname === "localhost" || u.hostname.includes(".")
    } catch {
      return false
    }
  }

  async function handleConvert() {
    setLoading(true)
    setResult("")
    setCopied(false)

    try {
      if (mode === "file") {
        if (!file) {
          toast.error("Please select a file")
          setLoading(false)
          return
        }
        let uploadFile = file
        if (isVideo(file.name)) {
          toast.info("Extracting audio from video\u2026")
          uploadFile = new File(
            [await extractAudio(file)],
            file.name.replace(/\.[^.]+$/, ".ogg"),
            { type: "audio/ogg" },
          )
        }
        if (uploadFile.size > MAX_DIRECT_UPLOAD) {
          toast.info("Uploading via Blob storage\u2026")
          const blobUrl = await uploadToBlob(uploadFile)
          toast.info("File uploaded, converting\u2026")
          const res = await fetch(`${API}/api/convert/blob`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              blob_url: blobUrl,
              filename: uploadFile.name,
              language: settings.sttLanguage,
            }),
          })
          if (!res.ok)
            throw new Error((await res.text()) || `Server error: ${res.status}`)
          const data = await res.json()
          setResult(data.markdown)
        } else {
          const form = new FormData()
          form.append("file", uploadFile)
          form.append("language", settings.sttLanguage)
          const ctrl = new AbortController()
          const t = setTimeout(() => ctrl.abort(), 180_000)
          const res = await fetch(`${API}/api/convert/file`, {
            method: "POST",
            body: form,
            signal: ctrl.signal,
          }).finally(() => clearTimeout(t))
          if (!res.ok)
            throw new Error((await res.text()) || `Server error: ${res.status}`)
          const data = await res.json()
          setResult(data.markdown)
        }
      } else {
        const trimmed = url.trim()
        if (!trimmed) {
          toast.error("Please enter a URL")
          setLoading(false)
          return
        }
        if (!isValidUrl(trimmed)) {
          toast.error("Please enter a valid URL (e.g. https://example.com)")
          setLoading(false)
          return
        }
        const res = await fetch(`${API}/api/convert/url`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: trimmed,
            language: settings.sttLanguage,
          }),
        })
        if (!res.ok)
          throw new Error((await res.text()) || `Server error: ${res.status}`)
        const data = await res.json()
        setResult(data.markdown)
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Conversion failed")
    } finally {
      setLoading(false)
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(result)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error("Failed to copy")
    }
  }

  return (
    <>
      <Toaster />
      <Header onSettingsToggle={() => setSidebarOpen((o) => !o)} />
      <div className="flex">
        <CollapsibleSidebar side="right" open={sidebarOpen}>
          <CollapsibleSidebarHeader>
            <Settings className="size-5 shrink-0" />
            <h2 className="text-sm font-semibold">Settings</h2>
          </CollapsibleSidebarHeader>
          <CollapsibleSidebarBody>
            <SettingsPanel settings={settings} onChange={updateSettings} />
          </CollapsibleSidebarBody>
        </CollapsibleSidebar>

        <main className="mx-auto max-w-4xl flex-1 space-y-6 px-4 py-8">
          <Card>
            <CardHeader>
              <div className="flex gap-1 rounded-lg bg-muted p-1">
                <button
                  type="button"
                  onClick={() => setMode("file")}
                  data-active={mode === "file" || undefined}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors cursor-pointer hover:bg-card data-[active]:bg-card data-[active]:shadow-sm"
                >
                  <HugeiconsIcon icon={File01Icon} className="size-4" />
                  Upload File
                </button>
                <button
                  type="button"
                  onClick={() => setMode("url")}
                  data-active={mode === "url" || undefined}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors cursor-pointer hover:bg-card data-[active]:bg-card data-[active]:shadow-sm"
                >
                  <HugeiconsIcon icon={LinkSquare02Icon} className="size-4" />
                  Convert URL
                </button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {mode === "file" ? (
                <>
                  <FileUpload value={file} onChange={setFile} />
                  {videoError && (
                    <p className="mt-2 text-sm text-destructive">{videoError}</p>
                  )}
                </>
              ) : (
                <UrlInput value={url} onChange={setUrl} onEnter={handleConvert} />
              )}
              <Button
                className="w-full cursor-pointer"
                onClick={handleConvert}
                disabled={
                  loading || !!(videoError) || (mode === "file" ? !file : !url.trim())
                }
              >
                {loading ? (
                  "Converting..."
                ) : (
                  <>
                    Convert to Markdown
                    <ArrowRight className="size-4" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Result</span>
                <div className="flex items-center gap-2">
                  {result && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCopy}
                      className="cursor-pointer gap-1"
                    >
                      {copied ? (
                        <>
                          <Check className="size-3.5" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="size-3.5" />
                          Copy
                        </>
                      )}
                    </Button>
                  )}
                  <div className="flex gap-0.5 rounded-lg bg-muted p-0.5">
                    <button
                      type="button"
                      onClick={() => setView("raw")}
                      data-active={view === "raw" || undefined}
                      className="rounded-md px-2.5 py-1 text-xs font-medium transition-colors cursor-pointer hover:bg-card data-[active]:bg-card data-[active]:shadow-sm"
                    >
                      Raw
                    </button>
                    <button
                      type="button"
                      onClick={() => setView("preview")}
                      data-active={view === "preview" || undefined}
                      className="rounded-md px-2.5 py-1 text-xs font-medium transition-colors cursor-pointer hover:bg-card data-[active]:bg-card data-[active]:shadow-sm"
                    >
                      Preview
                    </button>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {result ? (
                view === "raw" ? (
                  <Textarea
                    readOnly
                    value={result}
                    className="min-h-96 font-mono text-xs"
                  />
                ) : (
                  <div className="max-w-none overflow-x-auto rounded-lg border p-4 text-sm leading-relaxed [&_h1]:mb-3 [&_h1]:text-xl [&_h1]:font-bold [&_h2]:mb-2 [&_h2]:text-lg [&_h2]:font-semibold [&_h3]:mb-2 [&_h3]:text-base [&_h3]:font-semibold [&_p]:mb-2 [&_ul]:mb-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:mb-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_code]:rounded [&_code]:bg-muted [&_code]:px-1 [&_code]:py-0.5 [&_code]:text-xs [&_pre]:mb-3 [&_pre]:overflow-x-auto [&_pre]:rounded [&_pre]:bg-muted [&_pre]:p-3 [&_pre]:text-xs [&_blockquote]:mb-2 [&_blockquote]:border-l-2 [&_blockquote]:border-muted-foreground [&_blockquote]:pl-4 [&_blockquote]:italic [&_table]:mb-2 [&_table]:w-full [&_table]:text-left [&_th]:border [&_th]:border-border [&_th]:px-2 [&_th]:py-1 [&_th]:text-xs [&_td]:border [&_td]:border-border [&_td]:px-2 [&_td]:py-1 [&_td]:text-xs [&_a]:text-primary [&_a]:underline [&_img]:max-w-full [&_img]:rounded">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        img: ({ src, alt, ...props }) =>
                          src ? (
                            <img src={src} alt={alt ?? ""} {...props} />
                          ) : null,
                        table: ({ ...props }) => (
                          <div className="overflow-x-auto">
                            <table {...props} />
                          </div>
                        ),
                      }}
                    >
                      {result}
                    </ReactMarkdown>
                  </div>
                )
              ) : (
                <p className="py-12 text-center text-sm text-muted-foreground">
                  Convert something to see the result here
                </p>
              )}
            </CardContent>
          </Card>
        </main>
      </div>
    </>
  )
}
