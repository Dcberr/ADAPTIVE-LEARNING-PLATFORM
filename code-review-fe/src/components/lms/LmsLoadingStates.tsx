"use client"

import { Skeleton } from "@/components/ui/skeleton"

function PanelHeaderSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-8 w-48 rounded-full" />
      <Skeleton className="h-6 w-80 max-w-full rounded-full" />
    </div>
  )
}

function AttemptPanelSkeleton() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <Skeleton className="h-8 w-56 rounded-full" />
      <div className="mt-5 space-y-3">
        <Skeleton className="h-5 w-full rounded-full" />
        <Skeleton className="h-5 w-11/12 rounded-full" />
        <Skeleton className="h-5 w-4/5 rounded-full" />
      </div>
      <div className="mt-6 grid gap-3">
        <Skeleton className="h-20 w-full rounded-3xl" />
        <Skeleton className="h-20 w-full rounded-3xl" />
        <Skeleton className="h-20 w-full rounded-3xl" />
      </div>
    </div>
  )
}

export function AttemptWorkspaceSkeleton({
  title = "Đang tải bài làm...",
}: {
  title?: string
}) {
  return (
    <div className="space-y-4">
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <PanelHeaderSkeleton />
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-24 rounded-3xl" />
          <Skeleton className="h-24 rounded-3xl" />
          <Skeleton className="h-24 rounded-3xl" />
        </div>
        <p className="mt-4 text-sm text-slate-500">{title}</p>
      </div>
      <div className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
        <AttemptPanelSkeleton />
        <AttemptPanelSkeleton />
      </div>
    </div>
  )
}

export function AssignmentDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap gap-3">
          <Skeleton className="h-8 w-24 rounded-full" />
          <Skeleton className="h-8 w-32 rounded-full" />
          <Skeleton className="h-8 w-24 rounded-full" />
        </div>
        <Skeleton className="mt-5 h-10 w-96 max-w-full rounded-full" />
        <div className="mt-4 space-y-3">
          <Skeleton className="h-5 w-full rounded-full" />
          <Skeleton className="h-5 w-2/3 rounded-full" />
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Skeleton className="h-[280px] rounded-3xl" />
        <Skeleton className="h-[280px] rounded-3xl" />
      </div>
      <SubmissionHistorySkeleton />
    </div>
  )
}

export function SubmissionHistorySkeleton() {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {Array.from({ length: 2 }).map((_, index) => (
        <div
          key={index}
          className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <Skeleton className="h-8 w-36 rounded-full" />
          <Skeleton className="mt-3 h-5 w-44 rounded-full" />
          <div className="mt-5 space-y-3">
            {Array.from({ length: 5 }).map((__, row) => (
              <div
                key={row}
                className="grid grid-cols-[140px_1fr] gap-3 rounded-2xl bg-slate-50 px-4 py-3"
              >
                <Skeleton className="h-5 w-24 rounded-full" />
                <Skeleton className="h-5 w-full rounded-full" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export function CourseDetailSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-40 rounded-full" />
      <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <Skeleton className="h-56 w-full" />
        <div className="p-6">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-[1.2fr_0.8fr]">
            <Skeleton className="h-20 rounded-3xl" />
            <Skeleton className="h-20 rounded-3xl" />
          </div>
        </div>
      </div>
      <div className="space-y-4">
        <Skeleton className="h-12 w-72 rounded-full" />
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-40 rounded-3xl" />
          ))}
        </div>
      </div>
    </div>
  )
}

export function ClassWorkspaceSkeleton() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <PanelHeaderSkeleton />
        <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <Skeleton className="h-28 rounded-3xl" />
          <Skeleton className="h-28 rounded-3xl" />
        </div>
      </div>
      <div className="space-y-5">
        <Skeleton className="h-12 w-72 rounded-full" />
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="h-48 rounded-3xl" />
        ))}
      </div>
    </div>
  )
}

export function StudentsListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, index) => (
        <div
          key={index}
          className="rounded-2xl border border-slate-200 bg-white p-4"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <Skeleton className="size-12 rounded-full" />
              <div className="space-y-2">
                <Skeleton className="h-5 w-40 rounded-full" />
                <Skeleton className="h-4 w-56 rounded-full" />
                <div className="flex gap-2">
                  <Skeleton className="h-6 w-20 rounded-full" />
                  <Skeleton className="h-6 w-16 rounded-full" />
                </div>
              </div>
            </div>
            <Skeleton className="h-10 w-28 rounded-xl" />
          </div>
        </div>
      ))}
    </div>
  )
}
