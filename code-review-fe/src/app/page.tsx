"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

import { dashboardPathByRole, useAuthStore } from "@/store/authStore"

export default function Page() {
  const router = useRouter()
  const hasHydrated = useAuthStore((state) => state.hasHydrated)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const selectedRole = useAuthStore((state) => state.selectedRole ?? "student")

  useEffect(() => {
    if (!hasHydrated) {
      return
    }

    router.replace(isAuthenticated ? dashboardPathByRole[selectedRole] : "/login")
  }, [hasHydrated, isAuthenticated, router, selectedRole])

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f8f9fc]">
      <p className="text-sm font-medium text-[#030391]">Opening BK Learning Hub...</p>
    </div>
  )
}
