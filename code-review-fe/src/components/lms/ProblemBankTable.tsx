"use client"

import { useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { Search } from "lucide-react"

import type { ProblemBankEntry } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export default function ProblemBankTable({
  problems,
  isLoading = false,
  page = 0,
  size = 20,
}: {
  problems: ProblemBankEntry[]
  isLoading?: boolean
  page?: number
  size?: number
}) {
  const router = useRouter()
  const [query, setQuery] = useState("")

  const filtered = useMemo(() => {
    const normalized = query.toLowerCase()

    return problems.filter((problem) =>
      `${problem.title} ${(problem.tags ?? problem.topics).join(" ")}`
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

  const getDifficultyBadgeClassName = (value: ProblemBankEntry["difficulty"]) => {
    if (value === "EASY" || value === "Easy") {
      return "w-20 border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-50"
    }

    if (value === "MEDIUM" || value === "Medium") {
      return "w-20 border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-50"
    }

    if (value === "HARD" || value === "Hard") {
      return "w-20 border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-50"
    }

    return "w-20 border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-50"
  }

  const getTagBadgeClassName = (tag: string) => {
    const palette = [
      "border-sky-200 bg-sky-50 text-sky-700 hover:bg-sky-50",
      "border-cyan-200 bg-cyan-50 text-cyan-700 hover:bg-cyan-50",
      "border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-50",
      "border-violet-200 bg-violet-50 text-violet-700 hover:bg-violet-50",
      "border-teal-200 bg-teal-50 text-teal-700 hover:bg-teal-50",
      "border-fuchsia-200 bg-fuchsia-50 text-fuchsia-700 hover:bg-fuchsia-50",
    ]
    const index = Array.from(tag).reduce((sum, char) => sum + char.charCodeAt(0), 0) % palette.length

    return palette[index]
  }

  return (
    <>
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="pl-10"
          placeholder="Search by title or tag"
        />
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <Table className="min-w-[760px]">
          <TableHeader className="bg-slate-50/80">
            <TableRow className="hover:bg-slate-50/80">
              <TableHead className="w-16">STT</TableHead>
              <TableHead className="min-w-[320px]">Title</TableHead>
              <TableHead className="w-32">Difficulty</TableHead>
              <TableHead className="min-w-[220px]">Tags</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 6 }).map((_, index) => (
                <TableRow key={`problem-skeleton-${index}`} className="align-top">
                  <TableCell>
                    <Skeleton className="h-5 w-8 rounded-full" />
                  </TableCell>
                  <TableCell>
                    <div className="space-y-2">
                      <Skeleton className="h-5 w-56 rounded-full" />
                    </div>
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-6 w-20 rounded-full" />
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-2">
                      <Skeleton className="h-6 w-20 rounded-full" />
                      <Skeleton className="h-6 w-24 rounded-full" />
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : null}
            {!isLoading && filtered.length === 0 ? (
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={4} className="py-8 text-center text-slate-500">
                  Không có bài tập nào trong trang hiện tại.
                </TableCell>
              </TableRow>
            ) : null}
            {!isLoading
              ? filtered.map((problem, index) => (
              <TableRow
                key={problem.id}
                className="cursor-pointer align-top transition-colors hover:bg-slate-50/80"
                onClick={() => router.push(`/lecturer/problem-bank/${problem.id}`)}
              >
                <TableCell className="font-medium text-slate-500">
                  {(page * size + index + 1).toString().padStart(2, "0")}
                </TableCell>
                <TableCell>
                  <p className="font-semibold text-slate-900">{problem.title}</p>
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className={getDifficultyBadgeClassName(problem.difficulty)}>
                    {formatDifficultyLabel(problem.difficulty)}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-2">
                    {(problem.tags ?? problem.topics).length > 0 ? (
                      (problem.tags ?? problem.topics).map((tag) => (
                        <Badge key={tag} variant="outline" className={getTagBadgeClassName(tag)}>
                          {tag}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400">Chưa có tag</span>
                    )}
                  </div>
                </TableCell>
              </TableRow>
                ))
              : null}
          </TableBody>
        </Table>
      </div>
    </>
  )
}
