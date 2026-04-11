import { memo } from "react"
import { CalendarClock, Code2, FileCode2 } from "lucide-react"

import type { SubmissionRecord } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function SubmissionHistoryComponent({
  submissions,
}: {
  submissions: SubmissionRecord[]
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-[#030391]">Submission History</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
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
      </CardContent>
    </Card>
  )
}

const SubmissionHistory = memo(SubmissionHistoryComponent)

export default SubmissionHistory
