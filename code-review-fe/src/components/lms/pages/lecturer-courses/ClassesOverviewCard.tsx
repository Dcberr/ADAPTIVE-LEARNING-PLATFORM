"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function ClassesOverviewCard({
  classCount,
  enrolledStudentCount,
}: {
  classCount: number
  enrolledStudentCount: number
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl text-[#030391]">Managed Classes</CardTitle>
        <p className="text-sm text-slate-500">
          Open a class to manage topics, upload materials, configure coding assignments, and add
          students directly from the lecturer workspace.
        </p>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Classes</p>
          <p className="mt-2 text-3xl font-semibold text-[#030391]">{classCount}</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Students enrolled</p>
          <p className="mt-2 text-3xl font-semibold text-[#030391]">{enrolledStudentCount}</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Sync</p>
          <p className="mt-2 text-3xl font-semibold text-[#030391]">Live</p>
        </div>
      </CardContent>
    </Card>
  )
}
