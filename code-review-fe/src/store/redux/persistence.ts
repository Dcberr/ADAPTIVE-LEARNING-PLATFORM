import type { RootState } from "@/store/redux/store"

const AUTH_KEY = "bk-learning-auth"
const LMS_KEY = "bk-learning-lms"

function readStorage<T>(key: string): T | null {
  if (typeof window === "undefined") {
    return null
  }

  const raw = window.localStorage.getItem(key)

  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

function writeStorage<T>(key: string, value: T) {
  if (typeof window === "undefined") {
    return
  }

  window.localStorage.setItem(key, JSON.stringify(value))
}

export function loadPersistedAuthState() {
  return readStorage<RootState["auth"]>(AUTH_KEY)
}

export function loadPersistedLmsState() {
  return readStorage<RootState["lms"]>(LMS_KEY)
}

export function persistAuthState(state: RootState["auth"]) {
  writeStorage(AUTH_KEY, {
    selectedRole: state.selectedRole,
    isAuthenticated: state.isAuthenticated,
    user: state.user,
    hasHydrated: state.hasHydrated,
  })
}

export function persistLmsState(state: RootState["lms"]) {
  writeStorage(LMS_KEY, {
    problemBank: state.problemBank,
    topics: state.topics,
    materials: state.materials,
    submissions: state.submissions,
    hasHydrated: state.hasHydrated,
  })
}
