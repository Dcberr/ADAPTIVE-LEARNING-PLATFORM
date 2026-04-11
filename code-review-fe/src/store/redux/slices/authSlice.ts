import { createSlice, type PayloadAction } from "@reduxjs/toolkit"

import type { UserRole } from "@/data/lms/extendedMockData"

export type StoredUser = {
  id: string
  name: string
  email: string
  picture?: string | null
}

export type AuthSliceState = {
  selectedRole: UserRole | null
  isAuthenticated: boolean
  user: StoredUser | null
  hasHydrated: boolean
}

export const dashboardPathByRole: Record<UserRole, string> = {
  student: "/student/dashboard",
  lecturer: "/lecturer/dashboard",
}

const initialState: AuthSliceState = {
  selectedRole: "student",
  isAuthenticated: false,
  user: null,
  hasHydrated: false,
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    hydrateAuthState: (state, action: PayloadAction<Partial<AuthSliceState> | null>) => {
      if (action.payload) {
        state.selectedRole = action.payload.selectedRole ?? state.selectedRole
        state.isAuthenticated = action.payload.isAuthenticated ?? state.isAuthenticated
        state.user = action.payload.user ?? state.user
      }
    },
    setSelectedRole: (state, action: PayloadAction<UserRole>) => {
      state.selectedRole = action.payload
    },
    setSession: (
      state,
      action: PayloadAction<{ selectedRole: UserRole; user: StoredUser }>
    ) => {
      state.selectedRole = action.payload.selectedRole
      state.isAuthenticated = true
      state.user = action.payload.user
    },
    logout: (state) => {
      state.selectedRole = "student"
      state.isAuthenticated = false
      state.user = null
    },
    setHasHydrated: (state, action: PayloadAction<boolean>) => {
      state.hasHydrated = action.payload
    },
  },
})

export const authReducer = authSlice.reducer
export const authActions = authSlice.actions
