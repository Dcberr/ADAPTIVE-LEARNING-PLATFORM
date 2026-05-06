"use client"

import Link from "next/link"

import {
  AssignmentDetailSkeleton,
  SubmissionHistorySkeleton,
} from "@/components/lms/LmsLoadingStates"
import type { UserRole } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  useGetProblemByIdQuery,
  useGetProblemSubmissionsQuery,
} from "@/store/redux/api/lmsApi"

function formatDateTime(value?: string | null) {
  if (!value) {
    return "Chưa có dữ liệu"
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }

  return parsed.toLocaleString("vi-VN")
}

function formatScore(value?: string | null) {
  const numericScore = Number(value)

  if (!Number.isFinite(numericScore)) {
    return "Chưa có dữ liệu"
  }

  return `${numericScore.toLocaleString("vi-VN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}/100`
}

function formatRuntime(value?: number | null) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return null
  }

  return `${value} ms`
}

function formatDifficultyLabel(value: string) {
  if (value === "EASY") return "Dễ"
  if (value === "MEDIUM") return "Trung bình"
  if (value === "HARD") return "Khó"
  return value
}

export default function ProblemBankProblemDetailPage({
  id,
  role = "lecturer",
}: {
  id: string
  role?: UserRole
}) {
  const { data: problem, error, isLoading } = useGetProblemByIdQuery(id)
  const {
    data: submissions = [],
    isLoading: isLoadingSubmissions,
  } = useGetProblemSubmissionsQuery(id)

  if (isLoading) {
    return <AssignmentDetailSkeleton />
  }

  if (error || !problem) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Không tìm thấy bài luyện tập</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  const backHref = `/${role}/problem-bank`
  const attemptHref = `/${role}/problem-bank/${problem.id}/attempt`
  const bestScore = submissions.reduce((best, item) => {
    const score = Number(item.score)
    return Number.isFinite(score) ? Math.max(best, score) : best
  }, 0)
  const orderedSubmissions = [...submissions].sort((left, right) => {
    const leftTime = new Date(left.submittedAt).getTime()
    const rightTime = new Date(right.submittedAt).getTime()

    if (Number.isNaN(leftTime) || Number.isNaN(rightTime)) {
      return 0
    }

    return rightTime - leftTime
  })

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[#030391]/10 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <Badge className="bg-[#1488D8] text-white">Kho bài tập</Badge>
          <Badge variant="outline">{formatDifficultyLabel(problem.difficulty)}</Badge>
          <Badge variant="outline">100 điểm</Badge>
          {(problem.tags ?? []).map((tag) => (
            <Badge key={tag} className="bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
              {tag}
            </Badge>
          ))}
        </div>
        <h1 className="mt-4 text-3xl font-bold text-[#030391]">{problem.title}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl text-[#030391]">Thông tin bài làm</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-4 rounded-3xl bg-slate-50 p-5">
            <div>
              <p className="text-sm font-semibold text-slate-500">Mở bài</p>
              <p className="mt-1 text-lg text-slate-900">Luôn sẵn sàng</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-500">Hạn nộp</p>
              <p className="mt-1 text-lg text-slate-900">Không giới hạn</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm font-semibold text-slate-500">Số lần nộp tối đa</p>
                <p className="mt-1 text-lg text-slate-900">Không giới hạn</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Còn lại</p>
                <p className="mt-1 text-lg text-slate-900">Không giới hạn</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Giới hạn thời gian</p>
                <p className="mt-1 text-lg text-slate-900">Không giới hạn</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Điểm tối đa</p>
                <p className="mt-1 text-lg text-slate-900">100 điểm</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-[#1488D8]/15 bg-[#f8fbff] p-5">
            <p className="text-sm font-semibold uppercase tracking-wide text-[#1488D8]">
              Tổng quan lần nộp
            </p>
            <p className="mt-3 text-5xl font-bold text-[#030391]">{bestScore}/100</p>
            <p className="mt-2 text-sm text-slate-500">
              {submissions.length > 0
                ? `Đã có ${submissions.length} lần nộp cho bài luyện tập này.`
                : "Chưa có lịch sử nộp bài."}
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Button asChild className="rounded-2xl bg-[#030391] px-6 text-white hover:bg-[#030391]/90">
                <Link href={attemptHref}>Bắt đầu</Link>
              </Button>
              <Link href={backHref}>
                <Button variant="outline" className="rounded-2xl">
                  Quay lại Problem Bank
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-[#030391]">Lịch sử làm bài</h2>
        {isLoadingSubmissions ? (
          <SubmissionHistorySkeleton />
        ) : submissions.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-sm text-slate-500">
              Chưa có lịch sử làm bài.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 xl:grid-cols-2">
            {orderedSubmissions.map((submission, index) => (
              <Card key={submission.submissionId} className="gap-4 py-5">
                <CardHeader className="px-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <CardTitle className="text-lg text-[#030391]">
                        Lần nộp {orderedSubmissions.length - index}
                      </CardTitle>
                      <p className="mt-2 text-sm text-slate-500">
                        Nộp lúc {formatDateTime(submission.submittedAt)}
                      </p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3 px-5 text-sm">
                  {[
                    { label: "Trạng thái", value: submission.status },
                    { label: "Ngôn ngữ", value: submission.language },
                    { label: "Điểm", value: formatScore(submission.score) },
                    { label: "Thời gian chạy", value: formatRuntime(submission.runtime) },
                  ]
                    .filter((item) => item.value)
                    .map((item) => (
                      <div
                        key={`${submission.submissionId}-${item.label}`}
                        className="grid grid-cols-[120px_1fr] gap-3 rounded-2xl bg-slate-50 px-4 py-3"
                      >
                        <p className="font-semibold text-slate-600">{item.label}</p>
                        <p className="text-slate-900">{item.value}</p>
                      </div>
                    ))}
                  <div className="pt-1">
                    <Button asChild variant="outline" className="w-full rounded-2xl">
                      <Link href={`/${role}/problem-bank/${problem.id}/submissions/${submission.submissionId}`}>
                        Xem lại bài làm
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
