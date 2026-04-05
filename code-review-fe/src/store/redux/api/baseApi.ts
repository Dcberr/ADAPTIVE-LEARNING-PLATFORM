import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react"

import { getBackendBaseUrl } from "@/lib/auth"

export const apiTagTypes = [
  "Auth",
  "Class",
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
    baseUrl: getBackendBaseUrl(),
    credentials: "include",
  }),
  tagTypes: [...apiTagTypes],
  endpoints: () => ({}),
})
