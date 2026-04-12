"use client"

import { memo } from "react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { StudentPerformanceRecord } from "@/data/lms/extendedMockData"

const statusClassName: Record<StudentPerformanceRecord["status"], string> = {
  "at-risk": "bg-amber-100 text-amber-700 hover:bg-amber-100",
  excelling: "bg-emerald-100 text-emerald-700 hover:bg-emerald-100",
  stable: "bg-slate-100 text-slate-700 hover:bg-slate-100",
}

function StudentsMonitoringTabComponent({
  students,
}: {
  students: StudentPerformanceRecord[]
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-[#030391]">Student monitoring</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {students.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center">
            <p className="font-medium text-[#030391]">Chưa có dữ liệu monitoring cho lớp này.</p>
          </div>
        ) : null}

        {students.map((student) => (
          <div key={student.id} className="rounded-2xl border border-slate-200 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold text-slate-900">{student.name}</p>
                <p className="mt-1 text-sm text-slate-500">{student.email}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">{student.averageScore}% average</Badge>
                <Badge className={statusClassName[student.status]}>{student.status}</Badge>
              </div>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {student.assignmentScores.map((score) => (
                <div key={score.assignmentId} className="rounded-xl bg-slate-50 p-3 text-sm">
                  <p className="font-medium text-[#030391]">{score.assignmentTitle}</p>
                  <p className="mt-1 text-slate-500">
                    Score {score.score} • {new Date(score.submittedAt).toLocaleString("en-GB")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

const StudentsMonitoringTab = memo(StudentsMonitoringTabComponent)

export default StudentsMonitoringTab
