"use client"

import { type ReactNode } from "react"
import { cn } from "@/lib/utils"

interface CollapsibleSidebarProps {
  side: "left" | "right"
  open: boolean
  children: ReactNode
}

export function CollapsibleSidebar({
  side,
  open,
  children,
}: CollapsibleSidebarProps) {
  return (
    <div
      className={cn(
        "flex shrink-0 flex-col border-border bg-sidebar overflow-hidden transition-[width] duration-300 ease-in-out",
        side === "left" ? "border-r" : "border-l",
        side === "right" ? "order-last" : "order-first",
        open ? "w-80" : "w-0",
      )}
    >
      <div
        className={cn(
          "flex min-w-80 flex-1 flex-col overflow-hidden transition-opacity duration-200",
          open ? "opacity-100 delay-100" : "opacity-0",
        )}
      >
        {children}
      </div>
    </div>
  )
}

interface CollapsibleSidebarHeaderProps {
  children: ReactNode
}

export function CollapsibleSidebarHeader({ children }: CollapsibleSidebarHeaderProps) {
  return (
    <div className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
      {children}
    </div>
  )
}

interface CollapsibleSidebarBodyProps {
  children: ReactNode
}

export function CollapsibleSidebarBody({ children }: CollapsibleSidebarBodyProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      {children}
    </div>
  )
}

interface CollapsibleSidebarFooterProps {
  children: ReactNode
}

export function CollapsibleSidebarFooter({ children }: CollapsibleSidebarFooterProps) {
  return (
    <div className="shrink-0 border-t px-4 py-3">
      {children}
    </div>
  )
}
