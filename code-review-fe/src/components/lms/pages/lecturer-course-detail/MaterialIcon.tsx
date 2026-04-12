"use client"

import { FileText, ImageIcon, Video } from "lucide-react"

import type { CourseMaterial } from "@/data/lms/extendedMockData"

export default function MaterialIcon({ type }: { type: CourseMaterial["type"] }) {
  if (type === "video") {
    return <Video className="size-5 text-sky-600" />
  }

  if (type === "image") {
    return <ImageIcon className="size-5 text-violet-600" />
  }

  return <FileText className="size-5 text-emerald-600" />
}
