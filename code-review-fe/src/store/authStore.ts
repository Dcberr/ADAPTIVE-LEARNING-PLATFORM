"use client"

import { useMemo } from "react"

import type { UserRole } from "@/data/lms/extendedMockData"
import { authActions, type StoredUser } from "@/store/redux/slices/authSlice"
import { useAppDispatch, useAppSelector } from "@/store/redux/hooks"
import { store, type RootState } from "@/store/redux/store"

type AuthStoreShape = {
  selectedRole: UserRole | null
  isAuthenticated: boolean
  user: StoredUser | null
  hasHydrated: boolean
  setSelectedRole: (role: UserRole) => void
  signInWithGoogle: (role: UserRole) => void
  logout: () => void
  setHasHydrated: (value: boolean) => void
}

export const dashboardPathByRole: Record<UserRole, string> = {
  student: "/student/dashboard",
  lecturer: "/lecturer/dashboard",
}

function buildAuthStoreApi(state: RootState, dispatch = store.dispatch): AuthStoreShape {
  return {
    selectedRole: state.auth.selectedRole,
    isAuthenticated: state.auth.isAuthenticated,
    user: state.auth.user,
    hasHydrated: state.auth.hasHydrated,
    setSelectedRole: (role) => dispatch(authActions.setSelectedRole(role)),
    signInWithGoogle: (role) => dispatch(authActions.signInWithGoogle(role)),
    logout: () => dispatch(authActions.logout()),
    setHasHydrated: (value) => dispatch(authActions.setHasHydrated(value)),
  }
}

export function useAuthStore<T = AuthStoreShape>(
  selector: (state: AuthStoreShape) => T = ((state: AuthStoreShape) => state as T)
) {
  const dispatch = useAppDispatch()
  const authState = useAppSelector((state) => state.auth)
  const api = useMemo(
    () => buildAuthStoreApi({ ...store.getState(), auth: authState }, dispatch),
    [authState, dispatch]
  )

  return selector(api)
}

useAuthStore.getState = () => buildAuthStoreApi(store.getState())
