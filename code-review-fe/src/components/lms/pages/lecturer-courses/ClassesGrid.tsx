"use client"

import Link from "next/link"
import { ArrowRight, Users } from "lucide-react"

import type { LecturerClassSummary } from "@/store/redux/api/lmsApi"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

function getStatusClassName(status: LecturerClassSummary["status"]) {
  const statusClasses: Record<string, string> = {
    PLANNED: "bg-slate-100 text-slate-700 hover:bg-slate-100",
    IN_PROGRESS: "bg-sky-100 text-sky-700 hover:bg-sky-100",
    COMPLETED: "bg-emerald-100 text-emerald-700 hover:bg-emerald-100",
  }

  return statusClasses[status] ?? "bg-violet-100 text-violet-700 hover:bg-violet-100"
}

export default function ClassesGrid({
  classes,
  isLoading,
  hasError,
  highlightedClassId,
  onRetry,
}: {
  classes: LecturerClassSummary[]
  isLoading: boolean
  hasError: boolean
  highlightedClassId: string | null
  onRetry: () => void
}) {
  if (hasError) {
    return (
      <Card>
        <CardContent className="flex flex-wrap items-center justify-between gap-4 p-6">
          <p className="text-sm text-rose-700">
            Không tải được danh sách lớp. Kiểm tra backend rồi thử lại.
          </p>
          <Button variant="outline" onClick={onRetry}>
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 lg:grid-cols-2">
        {Array.from({ length: 2 }).map((_, index) => (
          <Card key={index} className="border border-slate-200">
            <CardContent className="h-56 animate-pulse bg-slate-100" />
          </Card>
        ))}
      </div>
    )
  }

  if (classes.length === 0) {
    return (
      <Card>
        <CardContent className="px-6 py-10 text-center">
          <p className="text-lg font-semibold text-[#030391]">No classes yet.</p>
          <p className="mt-2 text-sm text-slate-500">
            Create your first class above to start managing content and students.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {classes.map((item) => (
        <Card
          key={item.id}
          className={`border ${
            highlightedClassId === item.id
              ? "border-emerald-300 shadow-lg shadow-emerald-100"
              : "border-slate-200"
          }`}
        >
          <CardContent className="p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <Badge className={getStatusClassName(item.status)}>{item.status}</Badge>
                <h3 className="mt-3 text-xl font-semibold text-[#030391]">{item.name}</h3>
                <p className="mt-2 text-sm text-slate-600">Managed by {item.instructorName}</p>
              </div>
              <Users className="size-6 text-[#1488D8]" />
            </div>
            <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-500">
              <span>{item.enrolledStudentsCount} students</span>
              <span>Status {item.status}</span>
              <span className="truncate">ID {item.id}</span>
            </div>
            <Link href={`/lecturer/courses/${item.id}`}>
              <Button className="mt-5 rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90">
                Open class <ArrowRight className="size-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
