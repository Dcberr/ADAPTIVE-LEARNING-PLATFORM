"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowRight, CheckCircle2 } from "lucide-react"

import { AuroraBackground } from "@/components/ui/shadcn-io/aurora-background"
import GoogleLoginButton from "@/components/lms/GoogleLoginButton"
import RoleSelector from "@/components/lms/RoleSelector"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { buildGoogleLoginUrl } from "@/lib/auth"
import { useAppDispatch, useAppSelector } from "@/store/redux/hooks"
import { authActions, dashboardPathByRole } from "@/store/redux/slices/authSlice"

const platformHighlights = [
  "Gợi ý bài tập thích ứng từ kho bài tập dùng chung",
  "Không gian làm bài kiểu LeetCode kèm phản hồi review code bằng AI",
  "Công cụ cho giảng viên để quản lý topic, tài liệu, theo dõi và bài nộp",
]

export default function LoginPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const [loading, setLoading] = useState(false)
  const { hasHydrated, isAuthenticated, selectedRole } = useAppSelector((state) => state.auth)
  const resolvedRole = selectedRole ?? "student"
  const resolvedRoleLabel = resolvedRole === "student" ? "Sinh viên" : "Giảng viên"

  useEffect(() => {
    if (hasHydrated && isAuthenticated) {
      router.replace(dashboardPathByRole[resolvedRole])
    }
  }, [hasHydrated, isAuthenticated, resolvedRole, router])

  const handleLogin = () => {
    setLoading(true)
    window.location.href = buildGoogleLoginUrl(resolvedRole)
  }

  return (
    <AuroraBackground className="bg-[#edf4ff] text-slate-950">
      <div className="relative z-10 mx-auto grid min-h-screen w-full max-w-6xl items-center gap-8 px-4 py-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[2rem] border border-white/70 bg-slate-950/90 p-8 text-white shadow-2xl shadow-[#030391]/20 backdrop-blur-xl md:p-10">
          <Badge className="mb-5 rounded-full bg-[#1488D8] px-3 py-1 text-white">
            BK Learning Hub
          </Badge>
          <h1 className="max-w-xl text-4xl font-bold leading-tight">
            Nền tảng học lập trình thích ứng: Phân tích kết quả và gợi ý bài tập tiếp theo dựa trên năng lực
          </h1>
          <p className="mt-4 max-w-2xl text-base text-white/75">
            Đề tài tập trung phát triển một công cụ phân tích kết quả làm bài lập trình của sinh viên, ứng dụng AI Agent để tự động review code, chỉ ra ưu/nhược điểm và gợi ý cải tiến. Công cụ còn có khả năng đề xuất bài tập tiếp theo phù hợp từ kho bài tập, dựa trên năng lực và tiến trình học tập của từng sinh viên, hướng tới mô hình học tập thích ứng.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {platformHighlights.map((item) => (
              <div
                key={item}
                className="rounded-3xl border border-white/10 bg-white/8 p-4 backdrop-blur"
              >
                <CheckCircle2 className="mb-3 size-5 text-[#7ed0ff]" />
                <p className="text-sm text-white/85">{item}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-[2rem] border border-white/80 bg-white/75 p-6 shadow-2xl backdrop-blur-xl md:p-8">
          <div className="mb-6">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-[#1488D8]">
              Đăng nhập
            </p>
            <h2 className="mt-3 text-xl font-bold text-[#030391]">
              Chọn vai trò trước khi xác thực
            </h2>
          </div>

          <RoleSelector
            value={resolvedRole}
            onChange={(role) => dispatch(authActions.setSelectedRole(role))}
          />

          <div className="mt-6 rounded-3xl border border-[#030391]/10 bg-[#f8fbff] p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Vai trò đã chọn</p>
                <p className="text-xl font-semibold text-[#030391]">{resolvedRoleLabel}</p>
              </div>
              <ArrowRight className="size-5 text-[#1488D8]" />
            </div>
            <GoogleLoginButton role={resolvedRole} loading={loading} onClick={handleLogin} />
            <Button
              type="button"
              variant="ghost"
              className="mt-3 w-full rounded-2xl text-[#030391] hover:bg-[#E3F2FD]"
              onClick={() =>
                dispatch(
                  authActions.setSelectedRole(
                    resolvedRole === "student" ? "lecturer" : "student"
                  )
                )
              }
            >
              Đổi vai trò
            </Button>
          </div>
        </section>
      </div>
    </AuroraBackground>
  )
}
