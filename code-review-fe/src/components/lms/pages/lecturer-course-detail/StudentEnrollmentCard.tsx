"use client"

import type { FormEvent } from "react"
import { LoaderCircle, UserPlus } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

export default function StudentEnrollmentCard({
  instructorName,
  enrolledStudentsCount,
  createdAt,
  schedule,
  userCode,
  recentStudentIds,
  isSubmitting,
  onUserCodeChange,
  onSubmit,
}: {
  instructorName: string
  enrolledStudentsCount: number
  createdAt: string
  schedule: string | null
  userCode: string
  recentStudentIds: string[]
  isSubmitting: boolean
  onUserCodeChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}) {
  return (
    <Card className="border border-slate-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base text-[#030391]">
          <UserPlus className="size-4 text-[#1488D8]" />
          Thêm sinh viên vào lớp
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
            value={userCode}
            onChange={(event) => onUserCodeChange(event.target.value)}
            placeholder="Nhập mã sinh viên để thêm vào lớp"
          />
          <Button
            type="submit"
            className="rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <LoaderCircle className="size-4 animate-spin" />
                Đang thêm...
              </>
            ) : (
              "Thêm sinh viên"
            )}
          </Button>
        </form>

        {recentStudentIds.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {recentStudentIds.map((item) => (
              <Badge
                key={item}
                className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100"
              >
                Đã thêm {item}
              </Badge>
            ))}
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
