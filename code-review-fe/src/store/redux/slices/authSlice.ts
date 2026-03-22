import { createSlice, type PayloadAction } from "@reduxjs/toolkit"

import type { UserRole } from "@/data/lms/extendedMockData"
import { lecturerProfile, studentProfile } from "@/data/lms/extendedMockData"

export type StoredUser = {
  id: string
  name: string
  email: string
}

export type AuthSliceState = {
  selectedRole: UserRole | null
  isAuthenticated: boolean
  user: StoredUser | null
  hasHydrated: boolean
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
      state.hasHydrated = true
    },
    setSelectedRole: (state, action: PayloadAction<UserRole>) => {
      state.selectedRole = action.payload
    },
    signInWithGoogle: (state, action: PayloadAction<UserRole>) => {
      state.selectedRole = action.payload
      state.isAuthenticated = true
      state.user = action.payload === "student" ? studentProfile : lecturerProfile
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
