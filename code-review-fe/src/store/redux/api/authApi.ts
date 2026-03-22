import type { UserRole } from "@/data/lms/extendedMockData"
import { baseApi } from "@/store/redux/api/baseApi"
import type { StoredUser } from "@/store/redux/slices/authSlice"

type LoginWithGoogleRequest = {
  role: UserRole
  googleToken: string
}

type AuthSessionResponse = {
  user: StoredUser | null
  selectedRole: UserRole | null
  isAuthenticated: boolean
}

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getMe: builder.query<AuthSessionResponse, void>({
      query: () => "/auth/me",
      providesTags: ["Auth"],
    }),
    loginWithGoogle: builder.mutation<AuthSessionResponse, LoginWithGoogleRequest>({
      query: (body) => ({
        url: "/auth/google",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Auth"],
    }),
    logout: builder.mutation<{ success: boolean }, void>({
      query: () => ({
        url: "/auth/logout",
        method: "POST",
      }),
      invalidatesTags: ["Auth"],
    }),
  }),
})

export const { useGetMeQuery, useLoginWithGoogleMutation, useLogoutMutation } = authApi
