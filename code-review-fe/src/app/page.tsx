"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

import { useAppSelector } from "@/store/redux/hooks"
import { dashboardPathByRole } from "@/store/redux/slices/authSlice"

export default function Page() {
  const router = useRouter()
  const { hasHydrated, isAuthenticated, selectedRole } = useAppSelector((state) => state.auth)
  const resolvedRole = selectedRole ?? "student"

  useEffect(() => {
    if (!hasHydrated) {
      return
    }

    router.replace(isAuthenticated ? dashboardPathByRole[resolvedRole] : "/login")
  }, [hasHydrated, isAuthenticated, resolvedRole, router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f8f9fc]">
      <p className="text-sm font-medium text-[#030391]">Opening BK Learning Hub...</p>
    </div>
  )
}
