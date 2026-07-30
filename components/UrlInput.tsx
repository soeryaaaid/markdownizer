"use client"

import { useRef } from "react"
import { Input } from "@/components/ui/input"
import { GridPattern } from "@/components/ui/grid-pattern"

export function UrlInput({
  value,
  onChange,
  onEnter,
}: {
  value: string
  onChange: (value: string) => void
  onEnter?: () => void
}) {
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div className="group/url relative block w-full overflow-hidden rounded-lg p-6 md:p-10">
      <div className="absolute inset-0 [mask-image:radial-gradient(ellipse_at_center,white,transparent)]">
        <GridPattern />
      </div>
      <div className="relative z-20 flex flex-col items-center">
        <p className="text-base font-bold text-neutral-700 dark:text-neutral-300">
          Enter URL
        </p>
        <p className="mt-2 text-base font-normal text-neutral-400 dark:text-neutral-400">
          Paste a link to any page, article, or YouTube video
        </p>
        <div className="mt-6 md:mt-10 flex min-h-40 w-full items-center justify-center">
          <div className="w-full max-w-xl">
            <Input
              ref={inputRef}
              type="url"
              placeholder="https://example.com/article"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  onEnter?.()
                }
              }}
              className="h-12 w-full text-base"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
