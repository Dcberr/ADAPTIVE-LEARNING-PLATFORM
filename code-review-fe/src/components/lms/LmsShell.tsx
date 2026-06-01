"use client"

import { useEffect, useMemo, useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
  Award,
  Bell,
  BookOpen,
  Calendar as CalendarIcon,
  ChevronDown,
  Clock,
  LogOut,
  Menu,
  Search,
  TrendingUp,
  User,
  X,
} from "lucide-react"

import {
  initialProblemBank,
  lecturerManagedCourses,
  studentPerformance,
  type UserRole,
} from "@/data/lms/extendedMockData"
import { assignments, calendarEvents } from "@/data/lms/mockData"
import ExternalAvatar from "@/components/lms/ExternalAvatar"
import { navItemsByRole } from "@/components/lms/navigation"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/toast-provider"
import { logoutCurrentSession } from "@/lib/auth"
import {
  buildNotificationsWebSocketUrl,
  fetchNotifications,
  fetchUnreadNotificationCount,
  markNotificationAsRead,
  type NotificationRealtimeMessage,
  type NotificationRecord,
} from "@/lib/notifications"
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
  const { toast } = useToast()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [isSigningOut, setIsSigningOut] = useState(false)
  const [notifications, setNotifications] = useState<NotificationRecord[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(true)
  const [markingIds, setMarkingIds] = useState<Set<string>>(new Set())
  const user = useAppSelector((state) => state.auth.user)
  const compactWorkspace =
    /^\/(student|lecturer)\/assignments\/[^/]+\/attempt$/.test(pathname) ||
    /^\/(student|lecturer)\/problem-bank\/[^/]+\/attempt$/.test(pathname) ||
    /^\/(student|lecturer)\/assignments\/[^/]+\/submissions\/[^/]+$/.test(pathname) ||
    /^\/(student|lecturer)\/problem-bank\/[^/]+\/submissions\/[^/]+$/.test(pathname)
  const navItems = navItemsByRole[role]
  const profileHref = role === "student" ? "/student/profile" : "/lecturer/profile"
  const roleLabel = role === "student" ? "Sinh viên" : "Giảng viên"
  const academicCodeLabel = role === "student" ? "MSSV" : "MSCB"
  const initials =
    user?.name
      ?.split(" ")
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase() ?? "BK"
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

  useEffect(() => {
    let cancelled = false

    async function loadNotifications() {
      try {
        const [notificationItems, unread] = await Promise.all([
          fetchNotifications(),
          fetchUnreadNotificationCount(),
        ])

        if (cancelled) {
          return
        }

        setNotifications(notificationItems)
        setUnreadCount(unread)
      } catch {
        if (!cancelled) {
          setNotifications([])
          setUnreadCount(0)
        }
      } finally {
        if (!cancelled) {
          setIsLoadingNotifications(false)
        }
      }
    }

    void loadNotifications()

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!user) {
      return
    }

    const socket = new WebSocket(buildNotificationsWebSocketUrl())

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as NotificationRealtimeMessage

        if (typeof message.unreadCount === "number") {
          setUnreadCount(message.unreadCount)
        }

        if (message.type === "notification.created" && message.notification) {
          setNotifications((current) => [
            message.notification!,
            ...current.filter((item) => item.id !== message.notification!.id),
          ])

          toast({
            title: message.notification.title,
            description: message.notification.message,
            tone: "info",
          })
        }

        if (message.type === "notification.read" && message.notificationId) {
          setNotifications((current) =>
            current.map((item) =>
              item.id === message.notificationId
                ? {
                    ...item,
                    read: true,
                    readAt: new Date().toISOString(),
                  }
                : item
            )
          )
        }
      } catch {
        // Ignore malformed realtime payloads so the shell stays responsive.
      }
    }

    socket.onerror = () => {
      socket.close()
    }

    return () => {
      socket.close()
    }
  }, [toast, user])

  const handleMarkNotificationAsRead = async (notificationId: string) => {
    if (markingIds.has(notificationId)) {
      return
    }

    setMarkingIds((current) => new Set(current).add(notificationId))

    try {
      const updatedNotification = await markNotificationAsRead(notificationId)
      setNotifications((current) =>
        current.map((item) => (item.id === updatedNotification.id ? updatedNotification : item))
      )
      setUnreadCount((current) => Math.max(0, current - 1))
    } catch {
      toast({
        description: "Không thể cập nhật trạng thái thông báo.",
        tone: "error",
      })
    } finally {
      setMarkingIds((current) => {
        const next = new Set(current)
        next.delete(notificationId)
        return next
      })
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
              <Link href="/" className="group flex items-center gap-3">
                <Image
                  src="/hcmut.png"
                  alt="BK Logo"
                  width={96}
                  height={96}
                  className="h-12 w-auto object-contain transition-transform group-hover:scale-105"
                  priority
                />
                <div className="hidden flex-col items-center justify-center sm:flex">
                  <h1 className="text-center text-sm font-bold tracking-tight text-[#1488D8]">
                    ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH
                  </h1>
                  <p className="text-center text-xl font-bold tracking-tight text-[#030391]">
                    TRƯỜNG ĐẠI HỌC BÁCH KHOA
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
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="relative size-11 rounded-xl transition-colors hover:bg-[#E3F2FD]"
                  >
                    <Bell className="size-5 text-[#030391]" />
                    <Badge className="absolute -right-1 -top-1 size-5 bg-[#1488D8] p-0 text-white">
                      {unreadCount}
                    </Badge>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-[360px] rounded-2xl p-2">
                  <div className="flex items-center justify-between px-3 py-2">
                    <div>
                      <p className="text-sm font-semibold text-[#030391]">Thông báo trực tiếp</p>
                      <p className="text-xs text-slate-500">Cập nhật theo thời gian thực</p>
                    </div>
                    <Badge className="bg-[#1488D8] text-white">{unreadCount}</Badge>
                  </div>
                  <DropdownMenuSeparator />
                  <div className="max-h-[380px] overflow-y-auto">
                    {isLoadingNotifications ? (
                      <div className="px-3 py-6 text-sm text-slate-500">Đang tải thông báo...</div>
                    ) : notifications.length === 0 ? (
                      <div className="px-3 py-6 text-sm text-slate-500">Chưa có thông báo nào.</div>
                    ) : (
                      notifications.slice(0, 8).map((notification) => (
                        <DropdownMenuItem
                          key={notification.id}
                          className={cn(
                            "flex cursor-default items-start gap-3 rounded-xl px-3 py-3",
                            !notification.read && "bg-[#E3F2FD]/60"
                          )}
                          onSelect={(event) => event.preventDefault()}
                        >
                          <div
                            className={cn(
                              "mt-1 size-2 rounded-full",
                              notification.read ? "bg-slate-300" : "bg-[#1488D8]"
                            )}
                          />
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-semibold text-[#030391]">
                              {notification.title}
                            </p>
                            <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-600">
                              {notification.message}
                            </p>
                            <p className="mt-2 text-[11px] uppercase tracking-[0.12em] text-slate-400">
                              {new Date(notification.createdAt).toLocaleString("vi-VN")}
                            </p>
                          </div>
                          {!notification.read ? (
                            <button
                              type="button"
                              className="rounded-lg px-2 py-1 text-[11px] font-medium text-[#1488D8] transition hover:bg-white"
                              disabled={markingIds.has(notification.id)}
                              onClick={() => void handleMarkNotificationAsRead(notification.id)}
                            >
                              {markingIds.has(notification.id) ? "..." : "Da doc"}
                            </button>
                          ) : null}
                        </DropdownMenuItem>
                      ))
                    )}
                  </div>
                </DropdownMenuContent>
              </DropdownMenu>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    type="button"
                    className="flex items-center gap-3 rounded-2xl p-2 pr-4 text-left transition-all hover:bg-[#E3F2FD]"
                  >
                    <ExternalAvatar
                      src={user?.picture}
                      alt={user?.name ?? "Avatar"}
                      className="size-10 rounded-2xl object-cover shadow-sm"
                      fallback={
                        <div className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#030391] to-[#1488D8] shadow-sm">
                          <span className="text-2xl font-semibold text-white">{initials}</span>
                        </div>
                      }
                    />
                    <div className="hidden min-w-0 text-left sm:block">
                      <p className="truncate text-[13px] font-semibold uppercase tracking-[0.04em] text-[#030391]">
                        {user?.name ?? "BK Learning Hub"}
                      </p>
                      <p className="text-[13px] text-slate-500">{roleLabel}</p>
                    </div>
                    <ChevronDown className="hidden size-5 text-slate-400 sm:block" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-72 rounded-2xl p-2">
                  <div className="flex items-center gap-3 px-3 py-2">
                    <ExternalAvatar
                      src={user?.picture}
                      alt={user?.name ?? "Avatar"}
                      className="size-12 rounded-2xl object-cover"
                      fallback={
                        <div className="flex size-12 items-center justify-center rounded-2xl bg-gradient-to-br from-[#030391] to-[#1488D8]">
                          <span className="text-lg font-semibold text-white">{initials}</span>
                        </div>
                      }
                    />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-[#030391]">
                        {user?.name ?? "BK Learning Hub"}
                      </p>
                      <p className="truncate text-xs text-slate-500">{user?.email ?? ""}</p>
                      <p className="mt-1 text-xs font-medium text-slate-600">
                        {academicCodeLabel}: {user?.userCode || "Chưa có mã"}
                      </p>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href={profileHref} className="cursor-pointer rounded-xl">
                      <User className="size-4 text-[#030391]" />
                      Hồ sơ
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    variant="destructive"
                    className="rounded-xl"
                    disabled={isSigningOut}
                    onClick={() => void handleLogout()}
                  >
                    <LogOut className="size-4" />
                    {isSigningOut ? "Đang đăng xuất..." : "Đăng xuất"}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
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
                    <Link href="/student/courses">
                      <Badge className="cursor-pointer bg-[#1488D8] text-xs text-white">
                        Mở khóa học
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
