"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowRight, CheckCircle2, ShieldCheck } from "lucide-react"

import type { UserRole } from "@/data/lms/extendedMockData"
import { AuroraBackground } from "@/components/ui/shadcn-io/aurora-background"
import GoogleLoginButton from "@/components/lms/GoogleLoginButton"
import RoleSelector from "@/components/lms/RoleSelector"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { dashboardPathByRole, useAuthStore } from "@/store/authStore"

const platformHighlights = [
  "Adaptive exercise recommendations from the shared problem bank",
  "LeetCode-style assignment workspace with AI review feedback",
  "Lecturer tools for topics, materials, monitoring, and submissions",
]

export default function LoginPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const hasHydrated = useAuthStore((state) => state.hasHydrated)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const selectedRole = useAuthStore((state) => state.selectedRole ?? "student")
  const setSelectedRole = useAuthStore((state) => state.setSelectedRole)
  const signInWithGoogle = useAuthStore((state) => state.signInWithGoogle)

  useEffect(() => {
    if (hasHydrated && isAuthenticated) {
      router.replace(dashboardPathByRole[selectedRole])
    }
  }, [hasHydrated, isAuthenticated, router, selectedRole])

  const handleLogin = async () => {
    const role: UserRole = selectedRole
    setLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 650))
    signInWithGoogle(role)
    router.push(dashboardPathByRole[role])
  }

  return (
    <AuroraBackground className="bg-[#edf4ff] text-slate-950">
      <div className="relative z-10 mx-auto grid min-h-screen w-full max-w-6xl items-center gap-8 px-4 py-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[2rem] border border-white/70 bg-slate-950/90 p-8 text-white shadow-2xl shadow-[#030391]/20 backdrop-blur-xl md:p-10">
          <Badge className="mb-5 rounded-full bg-[#1488D8] px-3 py-1 text-white">
            BK Learning Hub
          </Badge>
          <h1 className="max-w-xl text-4xl font-bold leading-tight">
            Adaptive programming practice for thesis-scale LMS workflows.
          </h1>
          <p className="mt-4 max-w-2xl text-base text-white/75">
            Students move through courses, materials, assignments, AI review, and recommended next
            exercises. Lecturers manage the same ecosystem from one shared interface.
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

          <div className="mt-8 flex flex-wrap items-center gap-3 text-sm text-white/75">
            <ShieldCheck className="size-4 text-[#7ed0ff]" />
            Mocked Google authentication is enabled when backend auth is not available.
          </div>
        </section>

        <section className="rounded-[2rem] border border-white/80 bg-white/75 p-6 shadow-2xl backdrop-blur-xl md:p-8">
          <div className="mb-6">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-[#1488D8]">
              Sign In
            </p>
            <h2 className="mt-3 text-3xl font-bold text-[#030391]">Choose role before authentication</h2>
            <p className="mt-2 text-sm text-slate-600">
              The selected role is persisted locally so routing can send you to the correct dashboard.
            </p>
          </div>

          <RoleSelector value={selectedRole} onChange={setSelectedRole} />

          <div className="mt-6 rounded-3xl border border-[#030391]/10 bg-[#f8fbff] p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Selected role</p>
                <p className="text-xl font-semibold text-[#030391]">{selectedRole}</p>
              </div>
              <ArrowRight className="size-5 text-[#1488D8]" />
            </div>
            <GoogleLoginButton role={selectedRole} loading={loading} onClick={handleLogin} />
            <Button
              type="button"
              variant="ghost"
              className="mt-3 w-full rounded-2xl text-[#030391] hover:bg-[#E3F2FD]"
              onClick={() => setSelectedRole(selectedRole === "student" ? "lecturer" : "student")}
            >
              Switch role
            </Button>
          </div>
        </section>
      </div>
    </AuroraBackground>
  )
}
