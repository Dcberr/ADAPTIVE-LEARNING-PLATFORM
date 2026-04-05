"use client"

import { LoaderCircle } from "lucide-react"

import type { UserRole } from "@/data/lms/extendedMockData"
import { Button } from "@/components/ui/button"

function GoogleMark() {
  return (
    <svg aria-hidden="true" viewBox="0 0 48 48" className="size-5">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.6 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5Z" />
      <path fill="#FF3D00" d="M6.3 14.7 12.9 19C14.7 14.6 18.9 12 24 12c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7Z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 10-2 13.5-5.2l-6.2-5.2C29.3 35.1 26.8 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.6 5.1C9.5 39.6 16.2 44 24 44Z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-1.1 3.1-3.2 5.6-6 7.3l6.2 5.2C39.1 37.1 44 31.3 44 24c0-1.3-.1-2.4-.4-3.5Z" />
    </svg>
  )
}

export default function GoogleLoginButton({
  role,
  loading,
  onClick,
}: {
  role: UserRole
  loading: boolean
  onClick: () => void
}) {
  const roleLabel = role === "student" ? "Sinh viên" : "Giảng viên"

  return (
    <Button
      type="button"
      onClick={onClick}
      disabled={loading}
      className="h-12 w-full rounded-2xl bg-white text-slate-900 shadow-lg hover:bg-white/95"
    >
      {loading ? <LoaderCircle className="size-4 animate-spin" /> : <GoogleMark />}
      {loading ? "Đang đăng nhập..." : `Tiếp tục với Google với vai trò ${roleLabel}`}
    </Button>
  )
}
