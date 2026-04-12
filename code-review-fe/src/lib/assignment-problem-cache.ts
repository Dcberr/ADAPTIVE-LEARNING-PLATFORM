type CachedAssignmentProblem = {
  description: string
  problemConstraint: string
  starterCodeCpp: string
  testcases: Array<{
    input: string
    expectedOutput: string
    explanation: string
    hidden: boolean
  }>
  tags: string[]
}

const STORAGE_KEY = "bk-learning-assignment-problems"

function readStorage() {
  if (typeof window === "undefined") {
    return {}
  }

  try {
    return JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? "{}") as Record<
      string,
      CachedAssignmentProblem
    >
  } catch {
    return {}
  }
}

function writeStorage(value: Record<string, CachedAssignmentProblem>) {
  if (typeof window === "undefined") {
    return
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
}

export function saveCachedAssignmentProblem(
  assignmentId: string,
  problem: CachedAssignmentProblem
) {
  const current = readStorage()
  current[assignmentId] = problem
  writeStorage(current)
}

export function getCachedAssignmentProblem(assignmentId: string) {
  return readStorage()[assignmentId] ?? null
}
