"use client"

import { useRef } from "react"
import { motion } from "motion/react"
import { HugeiconsIcon } from "@hugeicons/react"
import { Upload04Icon } from "@hugeicons/core-free-icons"
import { useDropzone } from "react-dropzone"
import { cn } from "@/lib/utils"
import { GridPattern } from "@/components/ui/grid-pattern"

export function FileUpload({
  value,
  onChange,
}: {
  value: File | null
  onChange: (file: File | null) => void
}) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (files: File[]) => {
    onChange(files[0] ?? null)
  }

  const { getRootProps, isDragActive } = useDropzone({
    multiple: false,
    noClick: true,
    onDrop: handleFile,
  })

  return (
    <div className="w-full" {...getRootProps()}>
      <motion.div
        onClick={() => inputRef.current?.click()}
        whileHover="animate"
        className="group/file relative block w-full cursor-pointer overflow-hidden rounded-lg p-6 md:p-10"
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          onChange={(e) => handleFile(Array.from(e.target.files || []))}
        />
        <div className="absolute inset-0 [mask-image:radial-gradient(ellipse_at_center,white,transparent)]">
          <GridPattern />
        </div>
        <div className="relative z-20 flex flex-col items-center">
          <p className="text-base font-bold text-neutral-700 dark:text-neutral-300">
            {value ? "File selected" : "Upload file"}
          </p>
          <p className="mt-2 text-base font-normal text-neutral-400 dark:text-neutral-400">
            {value
              ? value.name
              : "Drag or drop your files here or click to upload"}
          </p>
          <div className="mt-6 md:mt-10 flex min-h-40 w-full items-center justify-center">
            <div className="relative w-full max-w-xl">
              {value && (
                <motion.div
                  layoutId="file-upload"
                  className={cn(
                    "relative z-40 mx-auto flex w-full flex-col items-start justify-start overflow-hidden rounded-md bg-white p-4 md:h-24 dark:bg-neutral-900",
                    "shadow-sm",
                  )}
                >
                  <div className="flex w-full items-center justify-between gap-4">
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      layout
                      className="min-w-0 truncate text-base text-neutral-700 dark:text-neutral-300"
                    >
                      {value.name}
                    </motion.p>
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      layout
                      className="shadow-input w-fit shrink-0 rounded-lg bg-neutral-100 px-2 py-1 text-sm text-neutral-600 dark:bg-neutral-800 dark:text-white"
                    >
                      {(value.size / (1024 * 1024)).toFixed(2)} MB
                    </motion.p>
                  </div>
                  <div className="mt-2 flex w-full flex-col items-start justify-between text-sm text-neutral-600 md:flex-row md:items-center dark:text-neutral-400">
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      layout
                      className="rounded-md bg-gray-100 px-1 py-0.5 dark:bg-neutral-800"
                    >
                      {value.type || "unknown"}
                    </motion.p>
                    <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} layout>
                      modified{" "}
                      {new Date(value.lastModified).toLocaleDateString()}
                    </motion.p>
                  </div>
                </motion.div>
              )}
              {!value && (
                <motion.div
                  layoutId="file-upload"
                  variants={{
                    initial: { x: 0, y: 0 },
                    animate: { x: 20, y: -20, opacity: 0.9 },
                  }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  className={cn(
                    "relative z-40 mx-auto flex h-32 w-full max-w-[8rem] items-center justify-center rounded-md bg-white shadow-[0px_10px_50px_rgba(0,0,0,0.1)] group-hover/file:shadow-2xl dark:bg-neutral-900",
                  )}
                >
                  {isDragActive ? (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex flex-col items-center text-neutral-600"
                    >
                      Drop it
                      <HugeiconsIcon icon={Upload04Icon} className="size-4" />
                    </motion.p>
                  ) : (
                    <HugeiconsIcon
                      icon={Upload04Icon}
                      className="size-4 text-neutral-600 dark:text-neutral-300"
                    />
                  )}
                </motion.div>
              )}
              {!value && (
                <motion.div
                  variants={{
                    initial: { opacity: 0 },
                    animate: { opacity: 1 },
                  }}
                  className="absolute inset-0 z-30 mx-auto flex h-32 w-full max-w-[8rem] items-center justify-center rounded-md border border-dashed border-sky-400 bg-transparent opacity-0"
                />
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
