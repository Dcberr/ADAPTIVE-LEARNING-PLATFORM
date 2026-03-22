import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react"

export const apiTagTypes = [
  "Auth",
  "Course",
  "Topic",
  "Material",
  "Assignment",
  "Submission",
  "ProblemBank",
  "Student",
] as const

export const baseApi = createApi({
  reducerPath: "baseApi",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api",
    credentials: "include",
  }),
  tagTypes: [...apiTagTypes],
  endpoints: () => ({}),
})
