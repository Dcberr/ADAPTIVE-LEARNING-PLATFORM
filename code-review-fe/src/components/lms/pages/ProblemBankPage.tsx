"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"

import ProblemBankTable from "@/components/lms/ProblemBankTable"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useGetProblemBankQuery } from "@/store/redux/api/lmsApi"

export default function ProblemBankPage() {
  const [page, setPage] = useState(0)
  const size = 20
  const { data, isLoading, isFetching } = useGetProblemBankQuery({ page, size })
  const isTableLoading = isLoading || isFetching
  const problems = data?.content ?? []
  const totalPages = data?.totalPages ?? 0
  const totalElements = data?.totalElements ?? 0
  const hasPreviousPage = page > 0
  const hasNextPage = totalPages > 0 && page < totalPages - 1

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-2xl text-[#030391]">Problem Bank</CardTitle>
          <p className="text-sm text-slate-500">
            {isTableLoading ? "Đang tải..." : `Tổng số bài: ${totalElements}`}
          </p>
        </CardHeader>
        <CardContent>
          <ProblemBankTable problems={problems} isLoading={isTableLoading} />
          <div className="mt-4 flex items-center justify-between">
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
        </CardContent>
      </Card>
    </div>
  )
}
