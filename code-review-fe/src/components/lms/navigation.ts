import {
  Award,
  BookOpen,
  Calendar,
  FileText,
  Gauge,
  Home,
  Library,
  MessageSquare,
  User,
  type LucideIcon,
} from "lucide-react"

import type { UserRole } from "@/data/lms/extendedMockData"

export type NavItem = {
  name: string
  href: string
  icon: LucideIcon
}

export const studentNavItems: NavItem[] = [
  { name: "Trang chủ", href: "/student/dashboard", icon: Home },
  { name: "Khóa học", href: "/student/courses", icon: BookOpen },
  { name: "Bài tập", href: "/student/assignments", icon: FileText },
  { name: "Điểm số", href: "/student/grades", icon: Award },
  { name: "Lịch", href: "/student/calendar", icon: Calendar },
  { name: "Tin nhắn", href: "/student/messages", icon: MessageSquare },
  { name: "Hồ sơ", href: "/student/profile", icon: User },
]

export const lecturerNavItems: NavItem[] = [
  { name: "Dashboard", href: "/lecturer/dashboard", icon: Gauge },
  { name: "Lớp học", href: "/lecturer/courses", icon: BookOpen },
  { name: "Problem Bank", href: "/lecturer/problem-bank", icon: Library },
  { name: "Lịch", href: "/lecturer/calendar", icon: Calendar },
  { name: "Tin nhắn", href: "/lecturer/messages", icon: MessageSquare },
]

export const navItemsByRole: Record<UserRole, NavItem[]> = {
  student: studentNavItems,
  lecturer: lecturerNavItems,
}
