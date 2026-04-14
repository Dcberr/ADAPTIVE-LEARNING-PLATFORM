"use client"

import Link from "next/link"
import Editor from "@monaco-editor/react"
import { ChevronLeft, Lock } from "lucide-react"

import type { UserRole } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  useGetAssignmentContextQuery,
  useGetAssignmentSubmissionsQuery,
  useGetSubmissionByIdQuery,
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

export default function SubmissionReviewPage({
  assignmentId,
  submissionId,
  role,
}: {
  assignmentId: string
  submissionId: string
  role: UserRole
}) {
  const { data: assignment, isLoading: isLoadingAssignment, error: assignmentError } =
    useGetAssignmentContextQuery(assignmentId)
  const {
    data: submissions = [],
    isLoading: isLoadingSubmissions,
  } = useGetAssignmentSubmissionsQuery({
    assignmentId,
    scope: role === "student" ? "me" : "all",
  })
  const { data: submissionDetail, isLoading: isLoadingDetail, error: detailError } =
    useGetSubmissionByIdQuery(submissionId)

  const submission = submissions.find((item) => item.submissionId === submissionId)
  const backHref = `/${role}/assignments/${assignmentId}`

  if (isLoadingAssignment || isLoadingSubmissions || isLoadingDetail) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Đang tải bài làm đã nộp...</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  if (assignmentError || detailError || !assignment || !submission || !submissionDetail) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Không tìm thấy bài làm để xem lại</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Button asChild variant="outline">
            <Link href={backHref}>Quay lại assignment</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={backHref}>
            <ChevronLeft className="size-4" />
            Quay lại lịch sử làm bài
          </Link>
        </Button>
        <Badge className="bg-slate-200 text-slate-700 hover:bg-slate-200">
          <Lock className="mr-1 size-3" />
          Chế độ xem lại, không thể chỉnh sửa
        </Badge>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-slate-100 p-6">
        <div className="flex flex-wrap items-center gap-3">
          <Badge className="bg-[#030391] text-white">{assignment.className}</Badge>
          <Badge variant="outline">{assignment.topicTitle}</Badge>
          <Badge className="bg-slate-300 text-slate-700 hover:bg-slate-300">
            {submissionDetail.language}
          </Badge>
          <Badge className="bg-slate-300 text-slate-700 hover:bg-slate-300">
            {submission.status}
          </Badge>
        </div>
        <h1 className="mt-4 text-3xl font-bold text-slate-900">{assignment.title}</h1>
      </div>

      <Card className="border-slate-200 bg-white">
        <CardHeader>
          <CardTitle className="text-xl text-slate-900">Tóm tắt lần nộp</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-[1fr_280px]">
          <div className="grid gap-3 text-sm">
            {role === "lecturer" ? (
              <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-200 pb-3">
                <p className="font-semibold text-slate-600">Sinh viên</p>
                <p className="text-slate-900">{submission.studentName}</p>
              </div>
            ) : null}
            <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-200 pb-3">
              <p className="font-semibold text-slate-600">Thời điểm bắt đầu</p>
              <p className="text-slate-900">{formatDateTime(submission.startedAt)}</p>
            </div>
            <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-200 pb-3">
              <p className="font-semibold text-slate-600">Thời điểm nộp</p>
              <p className="text-slate-900">{formatDateTime(submission.submittedAt)}</p>
            </div>
            <div className="grid grid-cols-[220px_1fr] gap-3 border-b border-slate-200 pb-3">
              <p className="font-semibold text-slate-600">Trạng thái</p>
              <p className="text-slate-900">{submission.status}</p>
            </div>
            <div className="grid grid-cols-[220px_1fr] gap-3">
              <p className="font-semibold text-slate-600">Điểm</p>
              <p className="text-slate-900">{submission.score}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-slate-200 bg-slate-100">
        <CardHeader>
          <CardTitle className="text-xl text-slate-900">Mã nguồn đã nộp</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-hidden rounded-2xl border border-slate-300 bg-slate-200">
            <Editor
              height="480px"
              language={submissionDetail.language === "cpp" ? "cpp" : submissionDetail.language}
              value={submissionDetail.code}
              options={{
                readOnly: true,
                domReadOnly: true,
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbersMinChars: 3,
                scrollBeyondLastLine: false,
                wordWrap: "on",
                contextmenu: false,
              }}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="border-slate-200 bg-white">
        <CardHeader>
          <CardTitle className="text-xl text-slate-900">Kết quả test của lần nộp</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {submissionDetail.testcaseResults.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
              Submission này chưa có chi tiết testcase.
            </div>
          ) : (
            submissionDetail.testcaseResults.map((result) => (
              <div
                key={`${result.testcaseId}-${result.index}`}
                className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-semibold text-slate-900">Test {result.index}</p>
                  <Badge
                    className={
                      result.status === "ACCEPTED"
                        ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-100"
                        : "bg-rose-100 text-rose-700 hover:bg-rose-100"
                    }
                  >
                    {result.status}
                  </Badge>
                </div>
                <div className="mt-3 grid gap-2 text-sm text-slate-600">
                  <p>Input: {result.input}</p>
                  <p>Expected: {result.expectedOutput}</p>
                  <p>Output: {result.output || "-"}</p>
                  {result.error ? <p>Error: {result.error}</p> : null}
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}
