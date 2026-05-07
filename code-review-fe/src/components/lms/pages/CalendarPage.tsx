"use client"

import Link from "next/link"
import { useMemo, useState } from "react"
import {
  ChevronLeft,
  ChevronRight,
  Clock3,
  Calendar as CalendarIcon,
  MoreHorizontal,
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useGetAssignmentDeadlinesQuery } from "@/store/redux/api/lmsApi"
import { useAppSelector } from "@/store/redux/hooks"

const MONTH_NAMES = [
  "Tháng 1",
  "Tháng 2",
  "Tháng 3",
  "Tháng 4",
  "Tháng 5",
  "Tháng 6",
  "Tháng 7",
  "Tháng 8",
  "Tháng 9",
  "Tháng 10",
  "Tháng 11",
  "Tháng 12",
]

const DAY_NAMES = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"]

type CalendarAssignmentEvent = {
  id: string
  title: string
  topicTitle: string
  deadline: string
  startTime: string | null
  difficulty: string
  status: string
}

function formatDayKey(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  return `${year}-${month}-${day}`
}

function getDifficultyBadgeClass(difficulty: string) {
  switch (difficulty.toUpperCase()) {
    case "HARD":
      return "border-rose-200 bg-rose-50 text-rose-700"
    case "MEDIUM":
      return "border-amber-200 bg-amber-50 text-amber-700"
    default:
      return "border-emerald-200 bg-emerald-50 text-emerald-700"
  }
}

function formatTime(dateTime: string | null) {
  if (!dateTime) return "Chưa cấu hình"

  return new Date(dateTime).toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  })
}

function formatDateTime(dateTime: string) {
  return new Date(dateTime).toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function buildCalendarDays(currentDate: Date) {
  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()
  const firstDayOfMonth = new Date(year, month, 1)
  const startOffset = firstDayOfMonth.getDay()
  const startDate = new Date(year, month, 1 - startOffset)

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + index)
    return date
  })
}

function CalendarDay({
  day,
  currentMonth,
  todayKey,
  events,
  role,
}: {
  day: Date
  currentMonth: number
  todayKey: string
  events: CalendarAssignmentEvent[]
  role: "student" | "lecturer"
}) {
  const dayKey = formatDayKey(day)
  const isToday = dayKey === todayKey
  const isCurrentMonth = day.getMonth() === currentMonth

  return (
    <div
      className={[
        "flex min-h-32 flex-col rounded-2xl border p-2 transition-colors",
        isToday ? "border-[#1488D8] bg-[#F2F9FF]" : "border-slate-200 bg-white",
        isCurrentMonth ? "opacity-100" : "opacity-50",
      ].join(" ")}
    >
      <div className="mb-2 flex items-center justify-between">
        <span
          className={[
            "flex size-8 items-center justify-center rounded-full text-sm font-semibold",
            isToday ? "bg-[#030391] text-white" : "text-slate-700",
          ].join(" ")}
        >
          {day.getDate()}
        </span>
        {events.length > 0 ? (
          <span className="text-[11px] font-medium text-slate-400">{events.length} bài</span>
        ) : null}
      </div>

      <div className="space-y-1.5">
        {events.slice(0, 2).map((event) => (
          <Link
            key={event.id}
            href={`/${role}/assignments/${event.id}`}
            className="block rounded-xl bg-[#030391] px-2 py-1.5 text-[11px] font-medium text-white transition hover:bg-[#1488D8]"
            title={`${event.title} - hạn nộp ${formatDateTime(event.deadline)}`}
          >
            <span className="line-clamp-2">{event.title}</span>
          </Link>
        ))}
        {events.length > 2 ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                type="button"
                className="flex w-full items-center justify-between rounded-xl border border-dashed border-slate-200 px-2 py-1.5 text-[11px] font-medium text-slate-500 transition hover:border-[#1488D8] hover:text-[#1488D8]"
              >
                <span>+{events.length - 2} bài nữa</span>
                <MoreHorizontal className="size-3.5" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-80">
              {events.map((event) => (
                <DropdownMenuItem key={event.id} asChild>
                  <Link
                    href={`/${role}/assignments/${event.id}`}
                    className="flex flex-col items-start gap-1"
                  >
                    <span className="line-clamp-2 font-medium text-slate-900">{event.title}</span>
                    <span className="text-xs text-slate-500">{event.topicTitle}</span>
                    <span className="text-xs text-slate-500">
                      Hạn nộp {formatDateTime(event.deadline)}
                    </span>
                  </Link>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        ) : null}
      </div>
    </div>
  )
}

export default function CalendarPage() {
  const role = useAppSelector((state) => (state.auth.selectedRole ?? "student") as "student" | "lecturer")
  const [currentDate, setCurrentDate] = useState(() => {
    const now = new Date()
    return new Date(now.getFullYear(), now.getMonth(), 1)
  })

  const { data: deadlines = [], isLoading, isFetching } = useGetAssignmentDeadlinesQuery()

  const eventsByDate = useMemo(() => {
    return deadlines.reduce<Record<string, CalendarAssignmentEvent[]>>((acc, assignment) => {
      const key = formatDayKey(new Date(assignment.deadline))
      const item: CalendarAssignmentEvent = {
        id: assignment.id,
        title: assignment.title,
        topicTitle: assignment.topicTitle,
        deadline: assignment.deadline,
        startTime: assignment.startTime,
        difficulty: assignment.difficulty,
        status: assignment.status,
      }

      acc[key] ??= []
      acc[key].push(item)
      acc[key].sort((left, right) => new Date(left.deadline).getTime() - new Date(right.deadline).getTime())

      return acc
    }, {})
  }, [deadlines])

  const calendarDays = useMemo(() => buildCalendarDays(currentDate), [currentDate])
  const todayKey = formatDayKey(new Date())

  const upcomingEvents = useMemo(
    () =>
      [...deadlines]
        .filter((item) => new Date(item.deadline).getTime() >= Date.now())
        .sort((left, right) => new Date(left.deadline).getTime() - new Date(right.deadline).getTime())
        .slice(0, 6),
    [deadlines]
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-950">Lịch deadline bài tập</h1>
        </div>
        <div className="inline-flex items-center gap-2 rounded-2xl border border-[#D6E8F8] bg-[#F7FBFF] px-4 py-2 text-sm text-slate-600">
          <CalendarIcon className="size-4 text-[#1488D8]" />
          {isFetching ? "Đang cập nhật lịch..." : `${deadlines.length} bài tập có hạn nộp`}
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,2fr)_360px]">
        <Card className="border-[#DDE7F3] shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between gap-4 space-y-0">
            <CardTitle className="text-xl text-[#030391]">
              {MONTH_NAMES[currentDate.getMonth()]} {currentDate.getFullYear()}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                className="rounded-2xl"
                onClick={() =>
                  setCurrentDate(
                    new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1)
                  )
                }
              >
                <ChevronLeft className="size-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="rounded-2xl"
                onClick={() =>
                  setCurrentDate(
                    new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1)
                  )
                }
              >
                <ChevronRight className="size-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-7 gap-2">
              {DAY_NAMES.map((dayName) => (
                <div
                  key={dayName}
                  className="py-2 text-center text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  {dayName}
                </div>
              ))}
              {calendarDays.map((day) => {
                const key = formatDayKey(day)

                return (
                  <CalendarDay
                    key={key}
                    day={day}
                    currentMonth={currentDate.getMonth()}
                    todayKey={todayKey}
                    events={eventsByDate[key] ?? []}
                    role={role}
                  />
                )
              })}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card className="border-[#DDE7F3] shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg text-[#030391]">Sắp đến hạn</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {isLoading ? (
                <div className="rounded-2xl border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-500">
                  Đang tải lịch deadline...
                </div>
              ) : upcomingEvents.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-500">
                  Chưa có bài tập nào có hạn nộp.
                </div>
              ) : (
                upcomingEvents.map((event) => (
                  <Link
                    key={event.id}
                    href={`/${role}/assignments/${event.id}`}
                    className="block rounded-2xl border border-slate-200 p-4 transition hover:border-[#1488D8] hover:bg-[#F8FCFF]"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 space-y-2">
                        <p className="line-clamp-2 font-semibold text-slate-900">{event.title}</p>
                        <p className="text-sm text-slate-500">{event.topicTitle}</p>
                        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                          <span className="inline-flex items-center gap-1">
                            <Clock3 className="size-3.5" />
                            Hạn nộp {formatDateTime(event.deadline)}
                          </span>
                          {event.startTime ? (
                            <span>Bắt đầu {formatTime(event.startTime)}</span>
                          ) : null}
                        </div>
                      </div>
                      <Badge className={getDifficultyBadgeClass(event.difficulty)}>
                        {event.difficulty}
                      </Badge>
                    </div>
                  </Link>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
