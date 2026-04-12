"use client"

import Link from "next/link"
import { CalendarClock, FileCode2, ListChecks, TimerReset } from "lucide-react"

import type { UserRole } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  useGetAssignmentContextQuery,
  useGetAssignmentSubmissionsQuery,
} from "@/store/redux/api/lmsApi"

function formatDateTime(value?: string | null) {
  if (!value) {
    return "Chưa cấu hình"
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }

  return parsed.toLocaleString("vi-VN")
}

function formatScore(value?: number | null) {
  if (typeof value !== "number") {
    return "Chưa cấu hình"
  }

  return `${value} điểm`
}

function formatTimeLimit(value?: number | null) {
  if (typeof value !== "number") {
    return "Chưa cấu hình"
  }

  return `${value} phút`
}

export default function AssignmentDetailPage({
  id,
  role = "student",
}: {
  id: string
  role?: UserRole
}) {
  const { data: assignment, error, isLoading } = useGetAssignmentContextQuery(id)
  const {
    data: submissions = [],
    isLoading: isLoadingSubmissions,
  } = useGetAssignmentSubmissionsQuery({
    assignmentId: id,
    scope: role === "student" ? "me" : "all",
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Đang tải bài tập...</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  if (error || !assignment) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Không tìm thấy bài tập</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  const backHref =
    role === "student"
      ? `/student/courses/${assignment.classId}`
      : `/lecturer/courses/${assignment.classId}`
  const attemptHref =
    role === "student"
      ? `/student/assignments/${assignment.id}/attempt`
      : `/lecturer/assignments/${assignment.id}/attempt`
  const bestScore = submissions.reduce((best, item) => {
    const score = Number(item.score)
    return Number.isFinite(score) ? Math.max(best, score) : best
  }, 0)
  const attemptsUsed = submissions.length
  const attemptsAllowed = assignment.maxSubmission ?? 0
  const attemptsLeft = attemptsAllowed > 0 ? Math.max(attemptsAllowed - attemptsUsed, 0) : null

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[#030391]/10 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <Badge className="bg-[#030391] text-white">{assignment.className}</Badge>
          <Badge variant="outline">{assignment.topicTitle}</Badge>
          <Badge variant="outline">{assignment.difficulty}</Badge>
          <Badge variant="outline">{formatScore(assignment.maxScore)}</Badge>
          {(assignment.tags ?? []).map((tag) => (
            <Badge key={tag} className="bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
              {tag}
            </Badge>
          ))}
        </div>
        <h1 className="mt-4 text-3xl font-bold text-[#030391]">{assignment.title}</h1>
        <p className="mt-3 max-w-3xl text-slate-600">
          Bài tập thuộc topic {assignment.topicTitle}. Lịch sử làm bài và các mốc thời gian được
          đồng bộ từ assignment hiện tại.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl text-[#030391]">Thông tin bài làm</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-4 rounded-3xl bg-slate-50 p-5">
            <div>
              <p className="text-sm font-semibold text-slate-500">Mở bài</p>
              <p className="mt-1 text-lg text-slate-900">{formatDateTime(assignment.startTime)}</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-500">Hạn nộp</p>
              <p className="mt-1 text-lg text-slate-900">{formatDateTime(assignment.deadline)}</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm font-semibold text-slate-500">Số lần nộp tối đa</p>
                <p className="mt-1 text-lg text-slate-900">{attemptsAllowed || "Không giới hạn"}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Còn lại</p>
                <p className="mt-1 text-lg text-slate-900">
                  {attemptsLeft === null ? "Không giới hạn" : attemptsLeft}
                </p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Time limit</p>
                <p className="mt-1 text-lg text-slate-900">{formatTimeLimit(assignment.timeLimit)}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Điểm tối đa</p>
                <p className="mt-1 text-lg text-slate-900">{formatScore(assignment.maxScore)}</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-[#1488D8]/15 bg-[#f8fbff] p-5">
            <p className="text-sm font-semibold uppercase tracking-wide text-[#1488D8]">
              Tổng quan lần nộp
            </p>
            <p className="mt-3 text-5xl font-bold text-[#030391]">
              {bestScore}
              {typeof assignment.maxScore === "number" ? `/${assignment.maxScore}` : ""}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              {attemptsUsed > 0
                ? `Đã có ${attemptsUsed} lần nộp ${role === "lecturer" ? "trong lớp này" : "của bạn"}.`
                : "Chưa có lịch sử nộp bài."}
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Button asChild className="rounded-2xl bg-[#030391] px-6 text-white hover:bg-[#030391]/90">
                <Link href={attemptHref}>Bắt đầu</Link>
              </Button>
              <Link href={backHref}>
                <Button variant="outline" className="rounded-2xl">
                  Quay lại khóa học
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-[#030391]">Lịch sử làm bài</h2>
        {isLoadingSubmissions ? (
          <Card>
            <CardContent className="py-10 text-center text-sm text-slate-500">
              Đang tải lịch sử nộp bài...
            </CardContent>
          </Card>
        ) : submissions.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-sm text-slate-500">
              Chưa có lịch sử làm bài.
            </CardContent>
          </Card>
        ) : (
          submissions.map((submission, index) => (
            <Card key={submission.submissionId}>
              <CardHeader>
                <CardTitle className="text-xl text-[#030391]">Lần nộp {index + 1}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-6 lg:grid-cols-[1fr_auto]">
                <div className="space-y-3 text-sm">
                  {role === "lecturer" ? (
                    <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                      <p className="font-semibold text-slate-700">Sinh viên</p>
                      <p>{submission.studentName}</p>
                    </div>
                  ) : null}
                  <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                    <p className="font-semibold text-slate-700">Trạng thái</p>
                    <p>{submission.status}</p>
                  </div>
                  <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                    <p className="font-semibold text-slate-700">Bắt đầu lúc</p>
                    <p>{formatDateTime(submission.startedAt)}</p>
                  </div>
                  <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                    <p className="font-semibold text-slate-700">Nộp lúc</p>
                    <p>{formatDateTime(submission.submittedAt)}</p>
                  </div>
                  <div className="grid grid-cols-[220px_1fr] gap-3">
                    <p className="font-semibold text-slate-700">Điểm</p>
                    <p>{submission.score}</p>
                  </div>
                </div>

                <div className="flex min-w-[240px] flex-col gap-3 rounded-3xl bg-slate-50 p-5">
                  <div className="inline-flex items-center gap-2 text-slate-600">
                    <ListChecks className="size-4" />
                    {assignment.topicTitle}
                  </div>
                  <div className="inline-flex items-center gap-2 text-slate-600">
                    <CalendarClock className="size-4" />
                    {formatDateTime(submission.submittedAt)}
                  </div>
                  <div className="inline-flex items-center gap-2 text-slate-600">
                    <TimerReset className="size-4" />
                    {submission.status}
                  </div>
                  <div className="inline-flex items-center gap-2 text-slate-600">
                    <FileCode2 className="size-4" />
                    Score {submission.score}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
