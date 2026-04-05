"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
  AlertTriangle,
  Award,
  Bell,
  BookOpen,
  Calendar as CalendarIcon,
  ChevronDown,
  Clock,
  Library,
  Menu,
  Search,
  TrendingUp,
  X,
} from "lucide-react"

import {
  initialProblemBank,
  lecturerManagedCourses,
  studentPerformance,
  type UserRole,
} from "@/data/lms/extendedMockData"
import { assignments, calendarEvents } from "@/data/lms/mockData"
import { navItemsByRole } from "@/components/lms/navigation"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { logoutCurrentSession } from "@/lib/auth"
import { cn } from "@/lib/utils"
import { daysUntil } from "@/components/lms/date"
import { useAppDispatch, useAppSelector } from "@/store/redux/hooks"
import { authActions } from "@/store/redux/slices/authSlice"

export default function LmsShell({
  children,
  role = "student",
}: {
  children: React.ReactNode
  role?: UserRole
}) {
  const pathname = usePathname()
  const router = useRouter()
  const dispatch = useAppDispatch()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [isSigningOut, setIsSigningOut] = useState(false)
  const user = useAppSelector((state) => state.auth.user)
  const compactWorkspace = /^\/student\/assignments\/[^/]+\/attempt$/.test(pathname)
  const navItems = navItemsByRole[role]
  const dashboardHref =
    role === "student" ? "/student/dashboard" : "/lecturer/dashboard"
  const profileHref = role === "student" ? "/student/profile" : "/lecturer/dashboard"
  const handleLogout = async () => {
    setIsSigningOut(true)

    try {
      await logoutCurrentSession()
    } finally {
      dispatch(authActions.logout())
      router.replace("/login")
      setIsSigningOut(false)
    }
  }

  const upcoming = useMemo(
    () =>
      assignments
        .filter((item) =>
          role === "student"
            ? item.status === "pending"
            : lecturerManagedCourses.some((course) => course.id === item.courseId)
        )
        .sort(
          (a, b) =>
            new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
        )
        .slice(0, 4),
    [role]
  )

  const weeklyEvents = useMemo(
    () =>
      [...calendarEvents]
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
        .slice(0, 4),
    []
  )

  const atRiskStudents = useMemo(
    () => studentPerformance.filter((student) => student.status === "at-risk"),
    []
  )

  return (
    <div className="min-h-screen bg-[#f8f9fc]">
      <header className="sticky top-0 z-50 border-b border-[#030391]/10 bg-white/80 shadow-sm backdrop-blur-xl">
        <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
          <div className="flex h-20 items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setMobileOpen((value) => !value)}
                className="rounded-xl p-2 transition-colors hover:bg-[#E3F2FD] lg:hidden"
              >
                {mobileOpen ? (
                  <X className="size-6 text-[#030391]" />
                ) : (
                  <Menu className="size-6 text-[#030391]" />
                )}
              </button>
              <Link href={dashboardHref} className="flex items-center gap-3">
                <div className="size-11 rounded-xl bg-gradient-to-br from-[#030391] to-[#1488D8]" />
                <div className="hidden sm:block">
                  <h1 className="text-sm font-bold tracking-tight text-[#1488D8]">
                    ĐẠI HỌC BÁCH KHOA
                  </h1>
                  <p className="text-lg font-bold tracking-tight text-[#030391]">
                    BK LEARNING HUB
                  </p>
                </div>
              </Link>
            </div>

            <div className="mx-8 hidden max-w-2xl flex-1 md:flex">
              <div className="relative w-full">
                <Search className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-gray-400" />
                <Input
                  type="search"
                  placeholder={
                    role === "student"
                      ? "Tìm kiếm khóa học, bài tập hoặc tài liệu..."
                      : "Tìm kiếm khóa học quản lý, bài tập, sinh viên..."
                  }
                  className="h-12 rounded-2xl border-none bg-[#f8f9fc] pl-12 pr-4 text-sm"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                className="relative size-11 rounded-xl transition-colors hover:bg-[#E3F2FD]"
              >
                <Bell className="size-5 text-[#030391]" />
                <Badge className="absolute -right-1 -top-1 size-5 bg-[#1488D8] p-0 text-white">
                  {role === "student" ? 3 : atRiskStudents.length}
                </Badge>
              </Button>
              <Link
                href={profileHref}
                className="flex items-center gap-3 rounded-2xl p-2 pr-4 transition-all hover:bg-[#E3F2FD]"
              >
                <div className="flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#030391] to-[#1488D8]">
                  <span className="text-sm font-semibold text-white">
                    {user?.name
                      ?.split(" ")
                      .slice(0, 2)
                      .map((part) => part[0])
                      .join("")
                      .toUpperCase() ?? "BK"}
                  </span>
                </div>
                <div className="hidden text-left sm:block">
                  <p className="text-sm font-semibold text-[#030391]">
                    {user?.name ?? "BK Learning Hub"}
                  </p>
                  <p className="text-xs capitalize text-gray-500">{role}</p>
                </div>
                <ChevronDown className="hidden size-4 text-gray-400 sm:block" />
              </Link>
              <Button
                variant="ghost"
                size="sm"
                className="hidden rounded-xl text-[#030391] hover:bg-[#E3F2FD] lg:inline-flex"
                disabled={isSigningOut}
                onClick={handleLogout}
              >
                {isSigningOut ? "Signing out..." : "Sign out"}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div
        className={cn(
          "mx-auto px-4 py-8 sm:px-6 lg:px-8",
          compactWorkspace ? "max-w-[1800px]" : "max-w-[1400px]"
        )}
      >
        <div className="flex flex-col gap-6 lg:flex-row">
          {!compactWorkspace ? (
            <aside
              className={cn(
                "shrink-0 lg:block lg:w-72",
                mobileOpen ? "block" : "hidden"
              )}
            >
            <nav className="mb-6 space-y-2 rounded-3xl border border-[#030391]/5 bg-white/70 p-3 shadow-lg backdrop-blur-xl">
              {navItems.map((item) => {
                const Icon = item.icon
                const active = pathname === item.href || pathname.startsWith(`${item.href}/`)

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-4 rounded-2xl px-5 py-4 text-[15px] font-medium transition-all",
                      active
                        ? "bg-gradient-to-r from-[#030391] to-[#030391]/90 text-white shadow-lg shadow-[#030391]/20"
                        : "text-gray-700 hover:bg-[#E3F2FD] hover:text-[#030391]"
                    )}
                  >
                    <Icon className="size-5" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </nav>

            {role === "student" ? (
              <>
                <div className="mb-6 rounded-3xl bg-gradient-to-br from-[#030391] to-[#1488D8] p-6 text-white shadow-xl">
                  <div className="mb-4 flex items-center gap-3">
                    <div className="flex size-12 items-center justify-center rounded-2xl bg-white/20">
                      <Award className="size-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold">Tiến độ học tập</h3>
                      <p className="text-xs text-white/80">Tiếp tục phát huy!</p>
                    </div>
                  </div>
                  <div className="space-y-4 text-sm">
                    <div>
                      <div className="mb-2 flex justify-between">
                        <span>Khóa học đã đăng ký</span>
                        <span className="font-bold">8</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/20">
                        <div className="h-full w-full rounded-full bg-white" />
                      </div>
                    </div>
                    <div>
                      <div className="mb-2 flex justify-between">
                        <span>Tiến độ tổng thể</span>
                        <span className="font-bold">64%</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/20">
                        <div className="h-full w-[64%] rounded-full bg-white" />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mb-6 rounded-3xl border border-[#030391]/5 bg-white/70 p-5 shadow-lg backdrop-blur-xl">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="font-bold text-[#030391]">Bài tập sắp tới</h3>
                    <Link href="/student/assignments">
                      <Badge className="cursor-pointer bg-[#1488D8] text-xs text-white">
                        Xem tất cả
                      </Badge>
                    </Link>
                  </div>
                  <div className="space-y-3">
                    {upcoming.map((item) => {
                      const remain = daysUntil(item.dueDate)
                      const urgent = remain <= 2
                      return (
                        <Link
                          key={item.id}
                          href={`/student/assignments/${item.id}`}
                          className="block"
                        >
                          <div
                            className={cn(
                              "rounded-xl border p-3 transition-all",
                              urgent
                                ? "border-[#1488D8]/30 bg-[#E3F2FD]"
                                : "border-gray-100 bg-white"
                            )}
                          >
                            <Badge className={`${item.courseColor} mb-2 text-xs text-white`}>
                              {item.courseName}
                            </Badge>
                            <h4 className="mb-1.5 line-clamp-2 text-sm font-medium text-[#030391]">
                              {item.title}
                            </h4>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <Clock className="size-3" />
                              {remain <= 0 ? "Hạn nộp hôm nay" : `Còn ${remain} ngày`}
                            </div>
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                </div>

                <div className="rounded-3xl border border-[#030391]/5 bg-white/70 p-5 shadow-lg backdrop-blur-xl">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="flex items-center gap-2 font-bold text-[#030391]">
                      <CalendarIcon className="size-5" />
                      Tuần này
                    </h3>
                    <Link href="/student/calendar">
                      <Badge className="cursor-pointer bg-[#1488D8] text-xs text-white">
                        Xem lịch
                      </Badge>
                    </Link>
                  </div>
                  <div className="space-y-3">
                    {weeklyEvents.map((event) => (
                      <div
                        key={event.id}
                        className="rounded-xl border border-[#1488D8]/20 bg-[#1488D8]/5 p-3"
                      >
                        <h4 className="text-sm font-semibold text-[#030391]">{event.title}</h4>
                        <p className="mt-1 text-xs text-gray-500">{event.time}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="mb-6 rounded-3xl bg-gradient-to-br from-[#030391] to-[#1488D8] p-6 text-white shadow-xl">
                  <div className="mb-4 flex items-center gap-3">
                    <div className="flex size-12 items-center justify-center rounded-2xl bg-white/20">
                      <TrendingUp className="size-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold">Teaching Pulse</h3>
                      <p className="text-xs text-white/80">Shared course and problem-bank overview</p>
                    </div>
                  </div>
                  <div className="space-y-4 text-sm">
                    <div>
                      <div className="mb-2 flex justify-between">
                        <span>Managed classes</span>
                        <span className="font-bold">{lecturerManagedCourses.length}</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/20">
                        <div className="h-full w-[75%] rounded-full bg-white" />
                      </div>
                    </div>
                    <div>
                      <div className="mb-2 flex justify-between">
                        <span>Bank problems</span>
                        <span className="font-bold">{initialProblemBank.length}</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/20">
                        <div className="h-full w-[82%] rounded-full bg-white" />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mb-6 rounded-3xl border border-[#030391]/5 bg-white/70 p-5 shadow-lg backdrop-blur-xl">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="flex items-center gap-2 font-bold text-[#030391]">
                      <BookOpen className="size-5" />
                      Class workload
                    </h3>
                    <Link href="/lecturer/courses">
                      <Badge className="cursor-pointer bg-[#1488D8] text-xs text-white">
                        Open classes
                      </Badge>
                    </Link>
                  </div>
                  <div className="space-y-3">
                    {upcoming.map((item) => {
                      const remain = daysUntil(item.dueDate)
                      return (
                        <div key={item.id} className="rounded-xl border border-gray-100 bg-white p-3">
                          <Badge className={`${item.courseColor} mb-2 text-xs text-white`}>
                            {item.courseName}
                          </Badge>
                          <h4 className="mb-1.5 line-clamp-2 text-sm font-medium text-[#030391]">
                            {item.title}
                          </h4>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Clock className="size-3" />
                            {remain <= 0 ? "Due today" : `${remain} day(s) left`}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div className="rounded-3xl border border-[#030391]/5 bg-white/70 p-5 shadow-lg backdrop-blur-xl">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="flex items-center gap-2 font-bold text-[#030391]">
                      <AlertTriangle className="size-5" />
                      At-risk students
                    </h3>
                    <Link href="/lecturer/problem-bank">
                      <Badge className="cursor-pointer bg-[#1488D8] text-xs text-white">
                        <Library className="mr-1 size-3" />
                        Problem bank
                      </Badge>
                    </Link>
                  </div>
                  <div className="space-y-3">
                    {atRiskStudents.map((student) => (
                      <div
                        key={student.id}
                        className="rounded-xl border border-amber-200 bg-amber-50 p-3"
                      >
                        <h4 className="text-sm font-semibold text-[#030391]">{student.name}</h4>
                        <p className="mt-1 text-xs text-gray-500">
                          Avg: {student.averageScore}% • Last submission{" "}
                          {new Date(student.lastSubmissionAt).toLocaleDateString("en-GB")}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            </aside>
          ) : null}

          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </div>
    </div>
  )
}
