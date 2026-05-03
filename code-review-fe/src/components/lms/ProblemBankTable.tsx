"use client"

import { useMemo, useState } from "react"
import { Search } from "lucide-react"

import type { ProblemBankEntry } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"

export default function ProblemBankTable({
  problems,
  isLoading = false,
}: {
  problems: ProblemBankEntry[]
  isLoading?: boolean
}) {
  const [query, setQuery] = useState("")

  const filtered = useMemo(() => {
    const normalized = query.toLowerCase()

    return problems.filter((problem) =>
      `${problem.title} ${problem.description} ${problem.topics.join(" ")}`
        .toLowerCase()
        .includes(normalized)
    )
  }, [problems, query])

  const formatDifficultyLabel = (value: ProblemBankEntry["difficulty"]) => {
    if (value === "EASY") return "Easy"
    if (value === "MEDIUM") return "Medium"
    if (value === "HARD") return "Hard"
    return value
  }

  return (
    <>
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="pl-10"
          placeholder="Search by title, description, or topic"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="border-b border-slate-200 text-slate-500">
            <tr>
              <th className="py-3 pr-4">Title</th>
              <th className="py-3 pr-4">Difficulty</th>
              <th className="py-3 pr-4">Topics</th>
              <th className="py-3 pr-4">Source</th>
              <th className="py-3 pr-4">Estimated minutes</th>
              <th className="py-3 pr-4">Recommended courses</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              Array.from({ length: 6 }).map((_, index) => (
                <tr key={`problem-skeleton-${index}`} className="border-b border-slate-100 align-top">
                  <td className="py-4 pr-4">
                    <div className="space-y-2">
                      <Skeleton className="h-5 w-56 rounded-full" />
                      <Skeleton className="h-4 w-40 rounded-full" />
                    </div>
                  </td>
                  <td className="py-4 pr-4">
                    <Skeleton className="h-6 w-20 rounded-full" />
                  </td>
                  <td className="py-4 pr-4">
                    <div className="flex flex-wrap gap-2">
                      <Skeleton className="h-6 w-20 rounded-full" />
                      <Skeleton className="h-6 w-24 rounded-full" />
                    </div>
                  </td>
                  <td className="py-4 pr-4">
                    <Skeleton className="h-5 w-16 rounded-full" />
                  </td>
                  <td className="py-4 pr-4">
                    <Skeleton className="h-5 w-12 rounded-full" />
                  </td>
                  <td className="py-4 pr-4">
                    <Skeleton className="h-5 w-24 rounded-full" />
                  </td>
                </tr>
              ))
            ) : null}
            {!isLoading && filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  Không có bài tập nào trong trang hiện tại.
                </td>
              </tr>
            ) : null}
            {!isLoading
              ? filtered.map((problem) => (
              <tr key={problem.id} className="border-b border-slate-100 align-top">
                <td className="py-4 pr-4">
                  <p className="font-semibold text-slate-900">{problem.title}</p>
                </td>
                <td className="py-4 pr-4">
                  <Badge variant="outline">{formatDifficultyLabel(problem.difficulty)}</Badge>
                </td>
                <td className="py-4 pr-4">
                  <div className="flex flex-wrap gap-2">
                    {problem.topics.map((topic) => (
                      <Badge key={topic} className="bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </td>
                <td className="py-4 pr-4 capitalize text-slate-600">{problem.source}</td>
                <td className="py-4 pr-4 text-slate-600">{problem.estimatedMinutes}</td>
                <td className="py-4 pr-4 text-slate-600">
                  {problem.recommendedForCourseIds.length > 0
                    ? problem.recommendedForCourseIds.join(", ")
                    : "Chưa có"}
                </td>
              </tr>
                ))
              : null}
          </tbody>
        </table>
      </div>
    </>
  )
}
