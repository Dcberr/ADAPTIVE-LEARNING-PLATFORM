"use client"

import Link from "next/link"
import { CalendarClock, FileCode2, PlayCircle, TimerReset } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getAssignmentOverview } from "@/services/lms/mockLmsService"

export default function AssignmentDetailPage({ id }: { id: string }) {
  const overview = getAssignmentOverview(id)

  if (!overview) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Không tìm thấy assignment</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  const attemptsLeft = Math.max(overview.attemptsAllowed - overview.attemptsUsed, 0)

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[#030391]/10 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <Badge className={`${overview.assignment.courseColor} text-white`}>
            {overview.assignment.courseName}
          </Badge>
          <Badge variant="outline">{overview.problem.difficulty}</Badge>
          <Badge variant="outline">{overview.assignment.points} points</Badge>
        </div>
        <h1 className="mt-4 text-3xl font-bold text-[#030391]">{overview.assignment.title}</h1>
        <p className="mt-3 max-w-3xl text-slate-600">{overview.problem.description.split("\n")[0]}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl text-[#030391]">Thông tin bài làm</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-4 rounded-3xl bg-slate-50 p-5">
            <div>
              <p className="text-sm font-semibold text-slate-500">Opened</p>
              <p className="mt-1 text-lg text-slate-900">
                {new Date(overview.openedAt).toLocaleString("vi-VN")}
              </p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-500">Closed</p>
              <p className="mt-1 text-lg text-slate-900">
                {new Date(overview.closedAt).toLocaleString("vi-VN")}
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm font-semibold text-slate-500">Attempts allowed</p>
                <p className="mt-1 text-lg text-slate-900">{overview.attemptsAllowed}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Attempts left</p>
                <p className="mt-1 text-lg text-slate-900">{attemptsLeft}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Thời gian làm bài</p>
                <p className="mt-1 text-lg text-slate-900">{overview.timeLimitMinutes} phút</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-500">Cách chấm điểm</p>
                <p className="mt-1 text-lg text-slate-900">{overview.gradingMethod}</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-[#1488D8]/15 bg-[#f8fbff] p-5">
            <p className="text-sm font-semibold uppercase tracking-wide text-[#1488D8]">
              Kết quả tốt nhất
            </p>
            <p className="mt-3 text-5xl font-bold text-[#030391]">
              {overview.bestScore}/{overview.assignment.points}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              {overview.attemptsUsed > 0
                ? `Bạn đã làm ${overview.attemptsUsed} lần.`
                : "Bạn chưa bắt đầu lần làm bài nào."}
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link href={`/student/assignments/${id}/attempt`}>
                <Button
                  disabled={attemptsLeft === 0}
                  className="rounded-2xl bg-[#030391] px-6 text-white hover:bg-[#030391]/90"
                >
                  <PlayCircle className="size-4" />
                  Bắt đầu
                </Button>
              </Link>
              <Link href="/student/assignments">
                <Button variant="outline" className="rounded-2xl">
                  Quay về danh sách
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-[#030391]">Tổng quan các lần làm bài trước</h2>
        {overview.submissions.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-sm text-slate-500">
              Chưa có lịch sử làm bài.
            </CardContent>
          </Card>
        ) : (
          overview.submissions.map((submission, index) => (
            <Card key={submission.id}>
              <CardHeader>
                <CardTitle className="text-xl text-[#030391]">Lần thử nghiệm {index + 1}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-6 lg:grid-cols-[1fr_auto]">
                <div className="space-y-3 text-sm">
                  <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                    <p className="font-semibold text-slate-700">Trạng thái</p>
                    <p>Đã xong</p>
                  </div>
                  <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                    <p className="font-semibold text-slate-700">Bắt đầu vào lúc</p>
                    <p>{new Date(submission.startedAt).toLocaleString("vi-VN")}</p>
                  </div>
                  <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                    <p className="font-semibold text-slate-700">Kết thúc lúc</p>
                    <p>{new Date(submission.finishedAt).toLocaleString("vi-VN")}</p>
                  </div>
                  <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-100 pb-3">
                    <p className="font-semibold text-slate-700">Thời gian thực hiện</p>
                    <p>{Math.max(1, Math.round(submission.durationSeconds / 60))} phút</p>
                  </div>
                  <div className="grid grid-cols-[220px_1fr] gap-3">
                    <p className="font-semibold text-slate-700">Điểm</p>
                    <p>
                      {submission.score} trên {overview.assignment.points} (
                      {Math.round((submission.score / overview.assignment.points) * 100)}%)
                    </p>
                  </div>
                </div>

                <div className="flex min-w-[240px] flex-col gap-3 rounded-3xl bg-slate-50 p-5">
                  <div className="inline-flex items-center gap-2 text-slate-600">
                    <TimerReset className="size-4" />
                    {submission.passed}/{submission.total} test passed
                  </div>
                  <div className="inline-flex items-center gap-2 text-slate-600">
                    <CalendarClock className="size-4" />
                    {submission.language}
                  </div>
                  <div className="inline-flex items-center gap-2 text-slate-600">
                    <FileCode2 className="size-4" />
                    {submission.code.split("\n").length} dòng code
                  </div>
                  <Link href={`/student/assignments/${id}/attempt`}>
                    <Button variant="outline" className="mt-3 w-full rounded-2xl">
                      Xem lại
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
