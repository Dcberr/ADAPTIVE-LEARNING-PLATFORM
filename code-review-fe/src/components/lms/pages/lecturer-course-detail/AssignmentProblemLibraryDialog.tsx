"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight, Search } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { useDebouncedValue } from "@/hooks/useDebouncedValue"
import { useGetProblemBankQuery } from "@/store/redux/api/lmsApi"

function formatDifficultyLabel(value: string) {
  if (value === "EASY") return "Dễ"
  if (value === "MEDIUM") return "Trung bình"
  if (value === "HARD") return "Khó"
  return value
}

function getDifficultyBadgeClassName(value: string) {
  if (value === "EASY" || value === "Easy") {
    return "w-20 justify-center border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-50"
  }

  if (value === "MEDIUM" || value === "Medium") {
    return "w-20 justify-center border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-50"
  }

  if (value === "HARD" || value === "Hard") {
    return "w-20 justify-center border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-50"
  }

  return "w-20 justify-center border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-50"
}

function getTagBadgeClassName(tag: string) {
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

export default function AssignmentProblemLibraryDialog({
  open,
  importingProblemId,
  onClose,
  onSelectProblem,
}: {
  open: boolean
  importingProblemId: string | null
  onClose: () => void
  onSelectProblem: (problemId: string) => void
}) {
  const [page, setPage] = useState(0)
  const [query, setQuery] = useState("")
  const debouncedQuery = useDebouncedValue(query)
  const size = 8
  const { data, isLoading, isFetching } = useGetProblemBankQuery(
    { page, size, q: debouncedQuery },
    { skip: !open }
  )
  const totalPages = data?.totalPages ?? 0
  const hasPreviousPage = page > 0
  const hasNextPage = totalPages > 0 && page < totalPages - 1
  const problems = data?.content ?? []

  return (
    <Dialog open={open} onOpenChange={(nextOpen) => (!nextOpen ? onClose() : undefined)}>
      <DialogContent className="grid h-[min(90vh,52rem)] max-h-[90vh] grid-rows-[auto_auto_minmax(0,1fr)_auto] gap-0 overflow-hidden p-0 sm:max-w-4xl">
        <DialogHeader className="shrink-0 border-b border-slate-100 px-8 py-6 pr-16">
          <DialogTitle>Chọn bài từ kho</DialogTitle>
          <DialogDescription>
            Chọn một bài trong kho bài tập để prefill vào form tạo assignment. Các trường còn thiếu
            vẫn có thể chỉnh tay trước khi lưu.
          </DialogDescription>
        </DialogHeader>

        <div className="shrink-0 px-8 py-5">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
            <Input
              value={query}
              onChange={(event) => {
                setQuery(event.target.value)
                setPage(0)
              }}
              className="pl-10"
              placeholder="Tìm theo tiêu đề hoặc tag"
            />
          </div>
        </div>

        <ScrollArea className="min-h-0">
          <div className="space-y-3 px-8 pb-6">
            {isLoading || isFetching ? (
              Array.from({ length: 6 }).map((_, index) => (
                <div
                  key={`problem-library-skeleton-${index}`}
                  className="rounded-2xl border border-slate-200 p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1 space-y-3">
                      <Skeleton className="h-5 w-2/3 rounded-full" />
                      <div className="flex gap-2">
                        <Skeleton className="h-6 w-20 rounded-full" />
                        <Skeleton className="h-6 w-24 rounded-full" />
                      </div>
                    </div>
                    <Skeleton className="h-10 w-28 rounded-xl" />
                  </div>
                </div>
              ))
            ) : null}

            {!isLoading && problems.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 px-6 py-10 text-center text-sm text-slate-500">
                Không có bài nào khớp với từ khóa hiện tại.
              </div>
            ) : null}

            {!isLoading
              ? problems.map((problem) => (
                  <div
                    key={problem.id}
                    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-[#1488D8]/35"
                  >
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                      <div className="min-w-0 flex-1 space-y-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge
                            variant="outline"
                            className={getDifficultyBadgeClassName(problem.difficulty)}
                          >
                            {formatDifficultyLabel(problem.difficulty)}
                          </Badge>
                          {(problem.tags ?? problem.topics).slice(0, 4).map((tag) => (
                            <Badge
                              key={`${problem.id}-${tag}`}
                              variant="outline"
                              className={getTagBadgeClassName(tag)}
                            >
                              {tag}
                            </Badge>
                          ))}
                        </div>

                        <div>
                          <p className="text-base font-semibold text-slate-900">{problem.title}</p>
                          <p className="mt-1 text-sm text-slate-500">
                            ID: <span className="font-mono text-xs">{problem.id}</span>
                          </p>
                        </div>
                      </div>

                      <Button
                        type="button"
                        className="rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90"
                        disabled={Boolean(importingProblemId)}
                        onClick={() => onSelectProblem(problem.id)}
                      >
                        {importingProblemId === problem.id ? "Đang nạp..." : "Dùng bài này"}
                      </Button>
                    </div>
                  </div>
                ))
              : null}
          </div>
        </ScrollArea>

        <div className="flex shrink-0 items-center justify-between border-t border-slate-100 px-8 py-4">
          <p className="text-sm text-slate-500">
            Trang {totalPages === 0 ? 0 : page + 1} / {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setPage((current) => Math.max(0, current - 1))}
              disabled={!hasPreviousPage || isFetching}
            >
              <ChevronLeft className="size-4" />
              Trước
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setPage((current) => current + 1)}
              disabled={!hasNextPage || isFetching}
            >
              Sau
              <ChevronRight className="size-4" />
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
