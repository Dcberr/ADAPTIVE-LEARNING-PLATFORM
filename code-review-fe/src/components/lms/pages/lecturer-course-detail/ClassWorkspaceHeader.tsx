"use client"

import Link from "next/link"
import { ArrowLeft, FilePenLine, Plus } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"

export default function ClassWorkspaceHeader({
  className,
  classDescription,
  classStatus,
  statusClassName,
  editMode,
  isRefreshing,
  onRefresh,
  onToggleEditMode,
  onAddSection,
}: {
  className: string
  classDescription: string
  classStatus: string
  statusClassName: string
  editMode: boolean
  isRefreshing: boolean
  onRefresh: () => void
  onToggleEditMode: () => void
  onAddSection: () => void
}) {
  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link href="/lecturer/courses">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 size-4" /> Back to Classes
          </Button>
        </Link>
        <div className="flex gap-3">
          <Button variant="outline" className="rounded-2xl" onClick={onRefresh}>
            {isRefreshing ? "Refreshing..." : "Refresh class"}
          </Button>
          <Button
            variant={editMode ? "default" : "outline"}
            className="rounded-2xl"
            onClick={onToggleEditMode}
          >
            <FilePenLine className="size-4" />
            {editMode ? "Thoát chỉnh sửa" : "Chỉnh sửa nội dung"}
          </Button>
          {editMode ? (
            <Button
              className="rounded-2xl bg-[#1488D8] text-white hover:bg-[#1488D8]/90"
              onClick={onAddSection}
            >
              <Plus className="size-4" />
              Add section
            </Button>
          ) : null}
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center gap-2">
            <Badge className="bg-[#030391] text-white">CLASS</Badge>
            <Badge className={statusClassName}>{classStatus}</Badge>
            <CardTitle className="text-2xl text-[#030391]">{className}</CardTitle>
          </div>
          <p className="text-sm text-slate-600">{classDescription}</p>
        </CardHeader>
      </Card>
    </>
  )
}
