"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

import type { UserRole } from "@/data/lms/extendedMockData"
import { useAppSelector } from "@/store/redux/hooks"

export default function AuthGuard({
  children,
  requiredRole,
}: {
  children: React.ReactNode
  requiredRole: UserRole
}) {
  const router = useRouter()
  const { hasHydrated, isAuthenticated, selectedRole } = useAppSelector((state) => state.auth)

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
