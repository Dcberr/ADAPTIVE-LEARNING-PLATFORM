import type { UserRole } from "@/data/lms/extendedMockData"
import type { StoredUser } from "@/store/redux/slices/authSlice"

type BackendRole = "STUDENT" | "INSTRUCTOR" | "ADMIN"

type BackendUser = {
  id: string
  email: string
  name: string
  userCode?: string | null
  picture?: string | null
  role: BackendRole
}

type ApiResponse<T> = {
  success: boolean
  message: string
  data: T
}

function trimTrailingSlash(value: string) {
  return value.endsWith("/") ? value.slice(0, -1) : value
}

export function getBackendBaseUrl() {
  const configuredBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim()

  if (configuredBaseUrl && configuredBaseUrl.startsWith("http")) {
    return trimTrailingSlash(configuredBaseUrl)
  }

  return "http://localhost:8080/api"
}

export function buildGoogleLoginUrl(role: UserRole) {
  const backendRole = role === "lecturer" ? "instructor" : "student"

  return `${getBackendBaseUrl()}/oauth2/authorization/google?role=${backendRole}`
}

export function mapBackendRoleToUserRole(role: BackendRole): UserRole {
  return role === "STUDENT" ? "student" : "lecturer"
}

export function mapBackendUserToStoredUser(user: BackendUser): StoredUser {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    userCode: user.userCode ?? null,
    picture: user.picture ?? null,
  }
}

export async function getCurrentUser() {
  const response = await fetch(`${getBackendBaseUrl()}/users/me`, {
    credentials: "include",
  })

  if (response.status === 401 || response.status === 403) {
    return null
  }

  if (!response.ok) {
    throw new Error("Unable to load current user")
  }

  const payload = (await response.json()) as ApiResponse<BackendUser>

  if (!payload.success || !payload.data) {
    throw new Error("Invalid current user response")
  }

  return {
    selectedRole: mapBackendRoleToUserRole(payload.data.role),
    user: mapBackendUserToStoredUser(payload.data),
  }
}

export async function logoutCurrentSession() {
  try {
    await fetch(`${getBackendBaseUrl()}/auth/logout`, {
      method: "POST",
      credentials: "include",
    })
  } catch {
    // Best-effort logout to support backends that expose a logout endpoint.
  }
}
