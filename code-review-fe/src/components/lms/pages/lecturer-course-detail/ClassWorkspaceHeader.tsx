"use client"

import Link from "next/link"
import { ArrowLeft, FilePenLine, Plus } from "lucide-react"

import { getClassCoverBackgroundImage } from "@/lib/class-cover"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function ClassWorkspaceHeader({
  classId,
  className,
  instructorName,
  enrolledStudentsCount,
  schedule,
  imageUrl,
  editMode,
  isRefreshing,
  onRefresh,
  onToggleEditMode,
  onAddSection,
}: {
  classId: string
  className: string
  instructorName: string
  enrolledStudentsCount: number
  schedule: string | null
  imageUrl?: string | null
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
            <ArrowLeft className="mr-2 size-4" /> Quay lại danh sách lớp
          </Button>
        </Link>
        <div className="flex gap-3">
          <Button variant="outline" className="rounded-2xl" onClick={onRefresh}>
            {isRefreshing ? "Đang làm mới..." : "Làm mới lớp"}
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
              Thêm section
            </Button>
          ) : null}
        </div>
      </div>

      <Card className="overflow-hidden gap-0 py-0">
        <div
          className="relative h-56 border-b border-slate-200 bg-slate-100 bg-cover bg-center"
          style={{
            backgroundImage: getClassCoverBackgroundImage({
              seed: classId,
              title: className,
              imageUrl,
            }),
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
          <div className="absolute bottom-6 left-6 text-white">
            <h1 className="text-xl font-semibold">{className}</h1>
            <p className="mt-2 text-lg text-gray-200">{instructorName}</p>
          </div>
        </div>
        <CardContent className="p-6">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-[1.2fr_0.8fr]">
            <div>
              <p className="text-sm text-gray-500">Lịch học</p>
              <p className="mt-2 text-xl font-medium text-slate-900">
                {schedule ?? "Chưa cấu hình"}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Sinh viên tham gia</p>
              <p className="mt-2 text-xl font-medium text-slate-900">
                {enrolledStudentsCount} sinh viên
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  )
}
