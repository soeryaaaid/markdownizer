"use client"

import { Button, buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { HugeiconsIcon } from "@hugeicons/react"
import { ApiIcon, Github01Icon, Settings01Icon } from "@hugeicons/core-free-icons"
import { useTheme } from "next-themes"

export function Header({
  onSettingsToggle,
}: {
  onSettingsToggle?: () => void
}) {
  const { setTheme, theme } = useTheme()

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center justify-between gap-4 px-4 border-b bg-background">
      <div className="flex items-center gap-3 shrink-0">
        <div className="p-1.5 rounded-lg border bg-muted">
          <img src="/markdown.svg" alt="Markdown" width="20" height="20" className="dark:invert" />
        </div>
        <div className="flex flex-col leading-none">
          <span className="text-sm font-bold">Markdownizer</span>
          <span className="text-[10px] text-muted-foreground">
            Anything to Markdown
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <a
          href="/api/docs"
          target="_blank"
          rel="noreferrer"
          aria-label="API Docs"
          className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "rounded-md cursor-pointer")}
        >
          <HugeiconsIcon icon={ApiIcon} className="size-4" />
        </a>

        <a
          href="https://github.com/soeryaaaid/markdownizer"
          target="_blank"
          rel="noreferrer"
          aria-label="GitHub Repository"
          className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "rounded-md cursor-pointer")}
        >
          <HugeiconsIcon icon={Github01Icon} className="size-4" />
        </a>

        <Button
          variant="ghost"
          size="icon"
          className="rounded-md cursor-pointer"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"
            strokeLinejoin="round" className="size-4">
            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
            <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
            <path d="M12 3l0 18" />
            <path d="M12 9l4.65 -4.65" />
            <path d="M12 14.3l7.37 -7.37" />
            <path d="M12 19.6l8.85 -8.85" />
          </svg>
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className="rounded-md cursor-pointer"
          onClick={onSettingsToggle}
          aria-label="Settings"
        >
          <HugeiconsIcon icon={Settings01Icon} className="size-4" />
        </Button>
      </div>
    </header>
  )
}
