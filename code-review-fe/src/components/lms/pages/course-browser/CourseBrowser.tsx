"use client"

import { useMemo, useState, type ReactNode } from "react"
import Link from "next/link"
import { ArrowRight, CalendarClock, Grid, List, Search, Users } from "lucide-react"

import { getClassCoverBackgroundImage } from "@/lib/class-cover"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"

export type CourseBrowserItem = {
  id: string
  href: string
  title: string
  instructor: string
  code?: string | null
  schedule?: string | null
  enrolledCount?: number | null
  imageUrl?: string | null
  seed: string
  actionLabel?: string
  highlighted?: boolean
}

type CourseBrowserProps = {
  items: CourseBrowserItem[]
  title: string
  emptyTitle: string
  emptyDescription: string
  searchPlaceholder: string
  headerActions?: ReactNode
  isLoading?: boolean
}

type ViewMode = "grid" | "list"

export default function CourseBrowser({
  items,
  title,
  emptyTitle,
  emptyDescription,
  searchPlaceholder,
  headerActions,
  isLoading = false,
}: CourseBrowserProps) {
  const [query, setQuery] = useState("")
  const [viewMode, setViewMode] = useState<ViewMode>("grid")

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()

    if (!normalizedQuery) {
      return items
    }

    return items.filter((item) => {
      const haystack = [item.title, item.code, item.instructor, item.schedule]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()

      return haystack.includes(normalizedQuery)
    })
  }, [items, query])

  return (
    <div className="space-y-6">
      <div className="rounded-[2rem] border border-[#005f69]/8 bg-white/80 p-6 shadow-lg shadow-slate-200/40 backdrop-blur-xl">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-[#0b6673]">{title}</h2>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant={viewMode === "grid" ? "default" : "outline"}
              size="icon"
              className={viewMode === "grid" ? "bg-[#0b6673] text-white hover:bg-[#0b6673]/90" : "rounded-xl"}
              onClick={() => setViewMode("grid")}
            >
              <Grid className="size-4" />
            </Button>
            <Button
              variant={viewMode === "list" ? "default" : "outline"}
              size="icon"
              className={viewMode === "list" ? "bg-[#0b6673] text-white hover:bg-[#0b6673]/90" : "rounded-xl"}
              onClick={() => setViewMode("list")}
            >
              <List className="size-4" />
            </Button>
            {headerActions}
          </div>
        </div>

        <div className="relative mt-5">
          <Search className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-slate-400" />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={searchPlaceholder}
            className="h-12 rounded-2xl border-slate-200 bg-slate-50 pl-12"
          />
        </div>
      </div>

      {filteredItems.length === 0 ? (
        isLoading ? (
          <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 6 }).map((_, index) => (
              <Card
                key={index}
                className="overflow-hidden gap-0 rounded-[2rem] border border-slate-200 bg-white py-0 shadow-md shadow-slate-200/50"
              >
                <Skeleton className="h-40 w-full rounded-none" />
                <CardContent className="space-y-4 p-5">
                  <div className="space-y-3">
                    <Skeleton className="h-8 w-3/4 rounded-full" />
                    <Skeleton className="h-5 w-1/2 rounded-full" />
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <Skeleton className="h-5 w-24 rounded-full" />
                    <Skeleton className="h-5 w-36 rounded-full" />
                  </div>
                  <Skeleton className="h-11 w-32 rounded-xl" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="rounded-[2rem] border border-slate-200">
            <CardContent className="px-6 py-12 text-center">
              <p className="text-lg font-semibold text-[#0b6673]">{emptyTitle}</p>
              <p className="mt-2 text-sm text-slate-500">{emptyDescription}</p>
            </CardContent>
          </Card>
        )
      ) : viewMode === "grid" ? (
        <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
          {filteredItems.map((item) => (
            <Link key={item.id} href={item.href} className="group block">
              <Card
                className={`h-full overflow-hidden gap-0! rounded-[2rem] border bg-white py-0 transition duration-200 hover:-translate-y-1 hover:shadow-xl ${
                  item.highlighted
                    ? "border-emerald-300 shadow-lg shadow-emerald-100"
                    : "border-slate-200 shadow-md shadow-slate-200/50"
                }`}
              >
                <div
                  className="relative h-40 bg-slate-100 bg-cover bg-center"
                  style={{
                    backgroundImage: getClassCoverBackgroundImage({
                      seed: item.seed,
                      title: item.title,
                      imageUrl: item.imageUrl,
                    }),
                  }}
                >
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/50 via-slate-900/10 to-white/5" />
                  {item.code ? (
                    <Badge className="absolute right-5 top-5 rounded-full bg-[#1717ad] px-4 py-2 text-sm text-white hover:bg-[#1717ad]">
                      {item.code}
                    </Badge>
                  ) : null}
                </div>
                <CardContent className="space-y-4 p-5">
                  <div>
                    <h3 className="line-clamp-2 text-xl font-bold leading-tight text-[#0b6673]">
                      {item.title}
                    </h3>
                    <p className="mt-2 text-base text-slate-500">{item.instructor}</p>
                  </div>
                  <div className="flex flex-wrap gap-x-6 gap-y-3 text-sm text-slate-600">
                    {typeof item.enrolledCount === "number" ? (
                      <span className="flex items-center gap-2">
                        <Users className="size-4" />
                        {item.enrolledCount} học viên
                      </span>
                    ) : null}
                    {item.schedule ? (
                      <span className="flex items-center gap-2">
                        <CalendarClock className="size-4" />
                        {item.schedule}
                      </span>
                    ) : null}
                  </div>
                  <div className="pt-1">
                    <span className="inline-flex items-center gap-2 rounded-xl bg-[#1717ad] px-4 py-2 text-sm font-medium text-white transition group-hover:bg-[#1717ad]/90">
                      {item.actionLabel ?? "Mở khóa học"} <ArrowRight className="size-4" />
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredItems.map((item) => (
            <Link key={item.id} href={item.href} className="group block">
              <Card
                className={`overflow-hidden rounded-[2rem] border bg-white py-0 transition hover:shadow-xl ${
                  item.highlighted
                    ? "border-emerald-300 shadow-lg shadow-emerald-100"
                    : "border-slate-200 shadow-md shadow-slate-200/50"
                }`}
              >
                <CardContent className="grid gap-5 p-5 lg:grid-cols-[280px_1fr_auto] lg:items-center">
                  <div
                    className="relative h-44 rounded-3xl bg-slate-100 bg-cover bg-center lg:h-36"
                    style={{
                      backgroundImage: getClassCoverBackgroundImage({
                        seed: item.seed,
                        title: item.title,
                        imageUrl: item.imageUrl,
                      }),
                    }}
                  >
                    <div className="absolute inset-0 rounded-3xl bg-gradient-to-t from-slate-950/45 via-slate-900/5 to-transparent" />
                    {item.code ? (
                      <Badge className="absolute left-4 top-4 rounded-full bg-[#1717ad] px-4 py-2 text-sm text-white hover:bg-[#1717ad]">
                        {item.code}
                      </Badge>
                    ) : null}
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h3 className="line-clamp-2 text-xl font-bold text-[#0b6673]">{item.title}</h3>
                      <p className="mt-2 text-lg text-slate-500">{item.instructor}</p>
                    </div>
                    <div className="flex flex-wrap gap-x-8 gap-y-3 text-sm text-slate-600">
                      {typeof item.enrolledCount === "number" ? (
                        <span className="flex items-center gap-2">
                          <Users className="size-4" />
                          {item.enrolledCount} học viên
                        </span>
                      ) : null}
                      {item.schedule ? (
                        <span className="flex items-center gap-2">
                          <CalendarClock className="size-4" />
                          {item.schedule}
                        </span>
                      ) : null}
                    </div>
                  </div>

                  <div className="flex justify-end lg:justify-start">
                    <span className="inline-flex items-center gap-2 rounded-xl bg-[#1717ad] px-4 py-2 text-sm font-medium text-white transition group-hover:bg-[#1717ad]/90">
                      {item.actionLabel ?? "Mở khóa học"} <ArrowRight className="size-4" />
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
