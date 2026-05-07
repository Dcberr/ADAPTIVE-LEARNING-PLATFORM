import { ChevronLeft, ChevronRight } from "lucide-react"

import { cn } from "@/lib/utils"

import { Button } from "@/components/ui/button"

type PaginationItem = number | "ellipsis"
const SIBLING_COUNT = 2

function buildPaginationItems(currentPage: number, totalPages: number): PaginationItem[] {
  if (totalPages <= 0) return []

  const pages = new Set<number>([0, totalPages - 1])

  for (let offset = -SIBLING_COUNT; offset <= SIBLING_COUNT; offset += 1) {
    const page = currentPage + offset
    if (page >= 0 && page < totalPages) {
      pages.add(page)
    }
  }

  const sortedPages = Array.from(pages).sort((left, right) => left - right)
  const items: PaginationItem[] = []

  for (const page of sortedPages) {
    const previousPage = typeof items[items.length - 1] === "number" ? items[items.length - 1] : null

    if (typeof previousPage === "number") {
      if (page - previousPage === 2) {
        items.push(previousPage + 1)
      } else if (page - previousPage > 2) {
        items.push("ellipsis")
      }
    }

    items.push(page)
  }

  return items
}

export default function CompactPagination({
  page,
  totalPages,
  onPageChange,
  disabled = false,
  className,
}: {
  page: number
  totalPages: number
  onPageChange: (page: number) => void
  disabled?: boolean
  className?: string
}) {
  const hasPreviousPage = page > 0
  const hasNextPage = totalPages > 0 && page < totalPages - 1
  const items = buildPaginationItems(page, totalPages)

  return (
    <div className={cn("flex flex-wrap items-center justify-center gap-2", className)}>
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => onPageChange(Math.max(0, page - 1))}
        disabled={!hasPreviousPage || disabled}
      >
        <ChevronLeft className="size-4" />
        Trước
      </Button>

      {items.map((item, index) =>
        item === "ellipsis" ? (
          <span
            key={`ellipsis-${index}`}
            className="flex h-8 min-w-8 items-center justify-center px-1 text-sm text-slate-500"
          >
            ...
          </span>
        ) : (
          <Button
            key={item}
            type="button"
            variant="outline"
            size="sm"
            className={cn(
              "min-w-8 px-2",
              item === page
                ? "border-[#030391] bg-[#030391] text-white hover:bg-[#030391]/90 hover:text-white"
                : "text-slate-600"
            )}
            onClick={() => onPageChange(item)}
            disabled={disabled}
            aria-current={item === page ? "page" : undefined}
          >
            {item + 1}
          </Button>
        )
      )}

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => onPageChange(Math.min(totalPages - 1, page + 1))}
        disabled={!hasNextPage || disabled}
      >
        Sau
        <ChevronRight className="size-4" />
      </Button>
    </div>
  )
}
