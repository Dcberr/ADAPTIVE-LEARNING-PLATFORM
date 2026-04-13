import { memo, useState } from "react"
import { CalendarClock, Code2, FileCode2, ListChecks } from "lucide-react"

import type { SubmissionRecord } from "@/data/lms/extendedMockData"
import {
  type AssignmentSubmissionResponse,
  useGetSubmissionByIdQuery,
} from "@/store/redux/api/lmsApi"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function MockSubmissionHistorySection({
  submissions,
}: {
  submissions: SubmissionRecord[]
}) {
  return (
    <>
      {submissions.map((submission) => (
        <div key={submission.id} className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <Badge className="bg-[#030391] text-white">{submission.language}</Badge>
                <Badge variant="outline">
                  {submission.passed}/{submission.total} tests
                </Badge>
                <Badge
                  className={
                    submission.score >= 70
                      ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-100"
                      : "bg-amber-100 text-amber-700 hover:bg-amber-100"
                  }
                >
                  Score {submission.score}
                </Badge>
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-500">
                <span className="inline-flex items-center gap-1">
                  <CalendarClock className="size-3" />
                  {new Date(submission.submittedAt).toLocaleString("en-GB")}
                </span>
                <span className="inline-flex items-center gap-1">
                  <FileCode2 className="size-3" />
                  {submission.status}
                </span>
              </div>
            </div>
            <div className="text-right text-sm text-slate-500">
              <div className="inline-flex items-center gap-1">
                <Code2 className="size-4" />
                {submission.code.split("\n").length} lines
              </div>
            </div>
          </div>
          <pre className="mt-4 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">
            <code>{submission.code}</code>
          </pre>
        </div>
      ))}
    </>
  )
}

function BackendSubmissionHistoryItem({
  submission,
}: {
  submission: AssignmentSubmissionResponse
}) {
  const [expanded, setExpanded] = useState(false)
  const { data, isFetching } = useGetSubmissionByIdQuery(submission.submissionId, {
    skip: !expanded,
  })
  const passedCount =
    data?.testcaseResults.filter((item) => item.status === "ACCEPTED").length ?? 0
  const totalCount = data?.testcaseResults.length ?? 0
  const numericScore = Number(submission.score)

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            {data?.language ? (
              <Badge className="bg-[#030391] text-white">{data.language}</Badge>
            ) : null}
            <Badge variant="outline">{submission.status}</Badge>
            <Badge
              className={
                Number.isFinite(numericScore) && numericScore >= 70
                  ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-100"
                  : "bg-amber-100 text-amber-700 hover:bg-amber-100"
              }
            >
              Score {submission.score}
            </Badge>
            {expanded && data ? (
              <Badge variant="outline">
                {passedCount}/{totalCount} tests
              </Badge>
            ) : null}
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-500">
            <span className="inline-flex items-center gap-1">
              <CalendarClock className="size-3" />
              {new Date(submission.submittedAt).toLocaleString("en-GB")}
            </span>
            <span className="inline-flex items-center gap-1">
              <ListChecks className="size-3" />
              Bắt đầu {new Date(submission.startedAt).toLocaleString("en-GB")}
            </span>
          </div>
        </div>

        <Button type="button" variant="outline" onClick={() => setExpanded((value) => !value)}>
          {expanded ? "Ẩn chi tiết" : "Xem chi tiết"}
        </Button>
      </div>

      {expanded ? (
        <div className="mt-4 space-y-4">
          {isFetching ? (
            <div className="rounded-2xl border border-dashed border-slate-300 p-4 text-sm text-slate-500">
              Đang tải chi tiết submission...
            </div>
          ) : null}

          {data?.code ? (
            <pre className="overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">
              <code>{data.code}</code>
            </pre>
          ) : null}

          {data?.testcaseResults?.length ? (
            <div className="space-y-3">
              {data.testcaseResults.map((result) => (
                <div
                  key={`${submission.submissionId}-${result.index}-${result.testcaseId}`}
                  className="rounded-2xl border border-slate-200 p-4 text-sm"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="font-medium text-slate-900">Test {result.index}</p>
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
                  <p className="mt-2 text-slate-600">Input: {result.input}</p>
                  <p className="mt-1 text-slate-600">Expected: {result.expectedOutput}</p>
                  <p className="mt-1 text-slate-600">Output: {result.output || result.error || "-"}</p>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}

function SubmissionHistoryComponent(
  props:
    | {
        variant: "mock"
        submissions: SubmissionRecord[]
      }
    | {
        variant: "backend"
        submissions: AssignmentSubmissionResponse[]
      }
) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-[#030391]">Submission History</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {props.submissions.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
            Chưa có submission nào.
          </div>
        ) : null}

        {props.variant === "mock" ? (
          <MockSubmissionHistorySection submissions={props.submissions} />
        ) : (
          props.submissions.map((submission) => (
            <BackendSubmissionHistoryItem
              key={submission.submissionId}
              submission={submission}
            />
          ))
        )}
      </CardContent>
    </Card>
  )
}

const SubmissionHistory = memo(SubmissionHistoryComponent)

export default SubmissionHistory
