"use client"

import { useState, useEffect } from "react"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { AppSettings } from "@/lib/settings"

const LOCALE_CODES = [
  "en-US", "en-GB", "en-AU", "en-IN",
  "id-ID", "ja-JP", "ko-KR", "zh-CN", "zh-TW", "zh-HK",
  "fr-FR", "fr-CA", "de-DE", "es-ES", "es-MX", "es-US",
  "pt-BR", "pt-PT", "ru-RU", "ar-SA", "ar-EG", "hi-IN",
  "it-IT", "nl-NL", "pl-PL", "tr-TR", "vi-VN", "th-TH",
  "ms-MY", "fil-PH", "sv-SE", "da-DK", "fi-FI", "nb-NO",
  "cs-CZ", "hu-HU", "ro-RO", "uk-UA", "el-GR", "he-IL",
]

const LANGUAGES = LOCALE_CODES.map((code) => ({
  value: code,
  label:
    new Intl.DisplayNames("en", { type: "language", languageDisplay: "dialect" }).of(code) ??
    code,
}))

export function SettingsPanel({
  settings,
  onChange,
}: {
  settings: AppSettings
  onChange: (s: AppSettings) => void
}) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="space-y-6 text-sm">
      <div className="space-y-2">
        <Label htmlFor="stt-language">Speech language</Label>
        <Select
          key={mounted ? "real" : "ssr"}
          items={LANGUAGES}
          value={mounted ? settings.sttLanguage : "en-US"}
          onValueChange={(v) => onChange({ ...settings, sttLanguage: v ?? "en-US" })}
        >
          <SelectTrigger id="stt-language" className="w-full cursor-pointer">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Languages</SelectLabel>
              {LANGUAGES.map((l) => (
                <SelectItem key={l.value} value={l.value} className={"cursor-pointer"}>
                  {l.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <p className="text-xs text-muted-foreground">
          Used by Groq Whisper for audio &amp; video transcription.
        </p>
      </div>


    </div>
  )
}
