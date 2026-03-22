"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

import type { UserRole } from "@/data/lms/extendedMockData"
import { useAuthStore } from "@/store/authStore"

export default function AuthGuard({
  children,
  requiredRole,
}: {
  children: React.ReactNode
  requiredRole: UserRole
}) {
  const router = useRouter()
  const hasHydrated = useAuthStore((state) => state.hasHydrated)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const selectedRole = useAuthStore((state) => state.selectedRole)

  useEffect(() => {
    if (!hasHydrated) {
      return
    }

    if (!isAuthenticated || selectedRole !== requiredRole) {
      router.replace("/login")
    }
  }, [hasHydrated, isAuthenticated, requiredRole, router, selectedRole])

  if (!hasHydrated || !isAuthenticated || selectedRole !== requiredRole) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f8f9fc]">
        <div className="rounded-3xl border border-[#030391]/10 bg-white px-8 py-6 text-center shadow-xl">
          <p className="text-sm font-medium text-[#030391]">Checking your LMS session...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
