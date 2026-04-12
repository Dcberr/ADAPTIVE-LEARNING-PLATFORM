"use client"

import { memo, useEffect, useState } from "react"
import Link from "next/link"
import { ChevronLeft, TimerReset } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { Assignment, CodingProblem } from "@/data/lms/mockData"

function formatRemaining(startedAtMs: number, timeLimitMinutes: number) {
  const elapsedSeconds = Math.floor((Date.now() - startedAtMs) / 1000)
  const remainingSeconds = Math.max(timeLimitMinutes * 60 - elapsedSeconds, 0)

  return `${String(Math.floor(remainingSeconds / 60)).padStart(2, "0")}:${String(
    remainingSeconds % 60
  ).padStart(2, "0")}`
}

function AssignmentAttemptHeaderComponent({
  assignment,
  problem,
  backHref,
  startedAtMs,
  timeLimitMinutes,
  language,
  languages,
  onLanguageChange,
}: {
  assignment: Assignment
  problem: CodingProblem
  backHref: string
  startedAtMs: number
  timeLimitMinutes: number
  language: string
  languages: readonly string[]
  onLanguageChange: (value: string) => void
}) {
  const [remainingMinutesLabel, setRemainingMinutesLabel] = useState(() =>
    formatRemaining(startedAtMs, timeLimitMinutes)
  )

  useEffect(() => {
    const interval = window.setInterval(() => {
      setRemainingMinutesLabel(formatRemaining(startedAtMs, timeLimitMinutes))
    }, 1000)

    return () => window.clearInterval(interval)
  }, [startedAtMs, timeLimitMinutes])

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={backHref}>
            <ChevronLeft className="size-4" /> Quay lại
          </Link>
        </Button>
        <div className="flex items-center gap-2">
          <div className="inline-flex items-center gap-2 rounded-2xl border border-[#1488D8]/20 bg-[#f8fbff] px-4 py-2 text-sm font-medium text-[#030391]">
            <TimerReset className="size-4 text-[#1488D8]" />
            Còn lại {remainingMinutesLabel}
          </div>
          <select
            value={language}
            onChange={(event) => onLanguageChange(event.target.value)}
            className="h-9 rounded-md border bg-background px-3 text-sm"
          >
            {languages.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="rounded-2xl border border-[#030391]/10 bg-white p-6">
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-2xl font-bold text-[#030391]">{problem.title}</h1>
          <Badge className={`${assignment.courseColor} text-white`}>{assignment.courseName}</Badge>
          <Badge variant="outline">{problem.difficulty}</Badge>
          <Badge variant="outline">{assignment.points} points</Badge>
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-600">
          <p className="max-w-3xl">{problem.description.split("\n")[0]}</p>
          <div className="flex gap-2">
            {problem.topics.map((topic) => (
              <Badge key={topic} className="bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
                {topic}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

const AssignmentAttemptHeader = memo(AssignmentAttemptHeaderComponent)

export default AssignmentAttemptHeader
