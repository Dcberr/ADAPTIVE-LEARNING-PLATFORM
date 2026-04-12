"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

import { Button } from "@/components/ui/button"
import { getCurrentUser } from "@/lib/auth"
import { useAppDispatch } from "@/store/redux/hooks"
import { authActions, dashboardPathByRole } from "@/store/redux/slices/authSlice"

export default function OAuthSuccessPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const [error, setError] = useState<string | null>(null)
  const hasRequestedSession = useRef(false)

  useEffect(() => {
    if (hasRequestedSession.current) {
      return
    }

    hasRequestedSession.current = true

    let cancelled = false

    void (async () => {
      try {
        const session = await getCurrentUser()

        if (cancelled) {
          return
        }

        if (!session) {
          dispatch(authActions.logout())
          setError("Google login succeeded, but no LMS user session was returned.")
          dispatch(authActions.setHasHydrated(true))
          return
        }

        dispatch(authActions.setSession(session))
        dispatch(authActions.setHasHydrated(true))
        router.replace(dashboardPathByRole[session.selectedRole])
      } catch {
        if (cancelled) {
          return
        }

        dispatch(authActions.logout())
        setError("Unable to complete Google sign-in. Please try again.")
        dispatch(authActions.setHasHydrated(true))
      }
    })()

    return () => {
      cancelled = true
    }
  }, [dispatch, router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f8f9fc] px-4">
      <div className="w-full max-w-md rounded-3xl border border-[#030391]/10 bg-white p-8 text-center shadow-xl">
        <h1 className="text-2xl font-bold text-[#030391]">Completing Google sign-in</h1>
        <p className="mt-3 text-sm text-slate-600">
          {error ?? "Your session is being restored from `/users/me`."}
        </p>

        {error ? (
          <Button asChild className="mt-6 rounded-2xl bg-[#030391] text-white hover:bg-[#02026f]">
            <Link href="/login">Back to login</Link>
          </Button>
        ) : (
          <div className="mt-6 flex items-center justify-center">
            <div className="size-10 animate-spin rounded-full border-4 border-[#1488D8]/20 border-t-[#1488D8]" />
          </div>
        )}
      </div>
    </div>
  )
}
