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
      <div className="flex min-h-screen items-center justify-center bg-[#f8f9fc] px-4">
        <div className="flex items-center justify-center rounded-3xl border border-[#030391]/10 bg-white px-8 py-8 shadow-xl">
          <div className="size-10 animate-spin rounded-full border-4 border-[#1488D8]/20 border-t-[#1488D8]" />
        </div>
      </div>
    )
  }

  return <>{children}</>
}
