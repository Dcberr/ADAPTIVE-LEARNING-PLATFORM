"use client"

import type { FormEvent } from "react"
import { LoaderCircle, UserPlus } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

type FeedbackState =
  | {
      tone: "success" | "error"
      message: string
    }
  | null

export default function StudentEnrollmentCard({
  instructorName,
  enrolledStudentsCount,
  createdAt,
  schedule,
  studentId,
  feedback,
  recentStudentIds,
  isSubmitting,
  onStudentIdChange,
  onSubmit,
}: {
  instructorName: string
  enrolledStudentsCount: number
  createdAt: string
  schedule: string | null
  studentId: string
  feedback: FeedbackState
  recentStudentIds: string[]
  isSubmitting: boolean
  onStudentIdChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}) {
  return (
    <Card className="border border-slate-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base text-[#030391]">
          <UserPlus className="size-4 text-[#1488D8]" />
          Add student to class
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 md:grid-cols-4">
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Instructor</p>
            <p className="mt-2 font-medium text-[#030391]">{instructorName}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Enrolled</p>
            <p className="mt-2 font-medium text-[#030391]">{enrolledStudentsCount}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Created</p>
            <p className="mt-2 font-medium text-[#030391]">{createdAt}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Schedule</p>
            <p className="mt-2 font-medium text-[#030391]">{schedule ?? "Chưa cấu hình"}</p>
          </div>
        </div>

        <form className="grid gap-3 md:grid-cols-[1fr_auto]" onSubmit={onSubmit}>
          <Input
            value={studentId}
            onChange={(event) => onStudentIdChange(event.target.value)}
            placeholder="Nhập student ID để thêm vào lớp"
          />
          <Button
            type="submit"
            className="rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <LoaderCircle className="size-4 animate-spin" />
                Adding...
              </>
            ) : (
              "Add student"
            )}
          </Button>
        </form>

        {feedback ? (
          <div
            className={`rounded-2xl border px-4 py-3 text-sm ${
              feedback.tone === "success"
                ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                : "border-rose-200 bg-rose-50 text-rose-700"
            }`}
          >
            {feedback.message}
          </div>
        ) : null}

        {recentStudentIds.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {recentStudentIds.map((item) => (
              <Badge
                key={item}
                className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100"
              >
                Added {item}
              </Badge>
            ))}
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
