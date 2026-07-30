const KEY = "markdownizer-settings"

export interface AppSettings {
  sttLanguage: string
}

const DEFAULTS: AppSettings = {
  sttLanguage: "en-US",
}

export function loadSettings(): AppSettings {
  if (typeof window === "undefined") return DEFAULTS
  try {
    const raw = localStorage.getItem(KEY)
    if (raw) return { ...DEFAULTS, ...JSON.parse(raw) }
  } catch {}
  return DEFAULTS
}

export function saveSettings(s: AppSettings) {
  try {
    localStorage.setItem(KEY, JSON.stringify(s))
  } catch {}
}
