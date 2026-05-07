import {
  baseCodeReviews,
  lecturerManagedCourses,
  studentPerformance,
  studentProfile,
  type CodeReviewFeedback,
  type ExecutionTestResult,
  type ProblemBankEntry,
  type StudentPerformanceRecord,
  type SubmissionRecord,
} from "@/data/lms/extendedMockData"
import { assignments, codingProblems, courses, type Assignment, type CodingProblem, type Course } from "@/data/lms/mockData"
import { useLmsStore } from "@/store/lmsStore"

const strategyKeywordsByProblemId: Record<string, string[]> = {
  "1": ["hash", "map", "dict", "object", "unordered_map"],
  "2": ["reverse", "10", "while", "mod"],
  "3": ["merge", "mid", "left", "right"],
}

type RunMode = "run" | "submit"
type Language = "python" | "javascript" | "java" | "cpp"
type SubmissionMeta = {
  startedAt?: string
  durationSeconds?: number
}

export type ExecutionSummary = {
  passed: number
  total: number
  percentage: number
  score: number
  results: ExecutionTestResult[]
  eligibleForReview: boolean
  status?: string
  errorMessage?: string | null
}

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
const gradingMethod = "Highest score"
const REVIEW_ELIGIBILITY_PERCENT = 30

function getAssignmentWindow(assignment: Assignment) {
  const closedAt = new Date(assignment.dueDate)
  const openedAt = new Date(closedAt.getTime() - 7 * 24 * 60 * 60 * 1000)
  const timeLimitMinutes =
    assignment.difficulty === "Hard" ? 60 : assignment.difficulty === "Medium" ? 45 : 30

  return {
    openedAt: openedAt.toISOString(),
    closedAt: closedAt.toISOString(),
    attemptsAllowed: 2,
    timeLimitMinutes,
    gradingMethod,
  }
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function getLatestSubmission(assignmentId: string) {
  return useLmsStore
    .getState()
    .submissions.find((submission) => submission.assignmentId === assignmentId)
}

function calculateConfidence(problem: CodingProblem, code: string, mode: RunMode) {
  const normalized = code.toLowerCase()
  const keywords = strategyKeywordsByProblemId[problem.id] ?? problem.topics.map((topic) => topic.toLowerCase())
  let confidence = 0.2

  if (normalized.length > 120) confidence += 0.12
  if (/(return|console\.log|print|cout)/.test(normalized)) confidence += 0.14
  if ((normalized.match(/\bfor\b|\bwhile\b/g) ?? []).length > 0) confidence += 0.12
  if (keywords.some((keyword) => normalized.includes(keyword))) confidence += 0.34
  if (!/pass|todo|viết code/.test(normalized)) confidence += 0.08
  if (mode === "submit") confidence += 0.08

  return clamp(confidence, 0.15, 0.96)
}

function simulateExecution(
  assignment: Assignment,
  problem: CodingProblem,
  code: string,
  mode: RunMode
): ExecutionSummary {
  const availableCases =
    mode === "run"
      ? problem.testCases.filter((testCase) => !testCase.hidden)
      : problem.testCases
  const confidence = calculateConfidence(problem, code, mode)
  const total = availableCases.length
  const passed = clamp(Math.round(confidence * total), 1, total)
  const results = availableCases.map((testCase, index) => ({
    idx: index + 1,
    input: testCase.input,
    expected: testCase.expectedOutput,
    actual: index < passed ? testCase.expectedOutput : "Unexpected output",
    passed: index < passed,
    hidden: testCase.hidden,
  }))

  const percentage = Math.round((passed / total) * 100)

  return {
    passed,
    total,
    percentage,
    score: Math.round((assignment.points * percentage) / 100),
    results,
    eligibleForReview: percentage >= REVIEW_ELIGIBILITY_PERCENT,
  }
}

function mergeDynamicReview(
  assignmentId: string,
  score: number,
  code: string
): CodeReviewFeedback {
  const problem = codingProblems.find((item) => item.assignmentId === assignmentId)
  const base =
    baseCodeReviews.find((item) => item.assignmentId === assignmentId) ??
    ({
      assignmentId,
      strengths: [],
      weaknesses: [],
      improvements: [],
    } satisfies CodeReviewFeedback)
  const normalized = code.toLowerCase()
  const hasStrategyKeyword = (strategyKeywordsByProblemId[problem?.id ?? ""] ?? []).some(
    (keyword) => normalized.includes(keyword)
  )

  return {
    assignmentId,
    strengths: [
      ...base.strengths,
      score >= 85
        ? "The solution is already close to production-level interview code for this difficulty."
        : "The code keeps the required function shape, which makes it easy to test and refine.",
    ],
    weaknesses: [
      ...base.weaknesses,
      hasStrategyKeyword
        ? "The implementation idea is good, but the edge-case handling still needs one more validation pass."
        : "The current approach still relies too much on the starter skeleton and needs a stronger core algorithm.",
    ],
    improvements: [
      ...base.improvements,
      score >= 70
        ? "Add a short complexity note or a helper extraction so the final submission reads more intentionally."
        : "Handle the simplest visible sample end-to-end first, then generalize and rerun the tests.",
    ],
  }
}

export async function getDashboardRouteForRole(role: "student" | "lecturer") {
  await wait(100)
  return role === "student" ? "/student/dashboard" : "/lecturer/dashboard"
}

export async function getStudentCourseTopics(courseId: string) {
  await wait(120)
  const state = useLmsStore.getState()

  return state.topics
    .filter((topic) => topic.courseId === courseId)
    .sort((a, b) => a.order - b.order)
    .map((topic) => ({
      ...topic,
      materials: state.materials.filter((material) => material.topicId === topic.id),
      assignments: assignments.filter((assignment) => topic.assignmentIds.includes(assignment.id)),
    }))
}

export async function getSubmissionHistory(assignmentId: string) {
  await wait(120)
  return useLmsStore
    .getState()
    .submissions.filter((submission) => submission.assignmentId === assignmentId)
}

export async function runAssignmentExecution(
  assignmentId: string,
  language: Language,
  code: string,
  mode: RunMode,
  meta?: SubmissionMeta
) {
  await wait(mode === "run" ? 450 : 700)
  const assignment = assignments.find((item) => item.id === assignmentId)
  const problem = codingProblems.find((item) => item.assignmentId === assignmentId)

  if (!assignment || !problem) {
    throw new Error("Assignment not found")
  }

  const summary = simulateExecution(assignment, problem, code, mode)

  if (mode === "submit") {
    const submission: SubmissionRecord = {
      id: `submission-${Date.now()}`,
      assignmentId,
      startedAt: meta?.startedAt ?? new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      submittedAt: new Date().toISOString(),
      finishedAt: new Date().toISOString(),
      durationSeconds: meta?.durationSeconds ?? 10 * 60,
      language,
      score: summary.score,
      passed: summary.passed,
      total: summary.total,
      status: summary.eligibleForReview ? "reviewed" : "submitted",
      code,
      testResults: summary.results,
    }

    useLmsStore.getState().addSubmission(submission)
  }

  return summary
}

export async function getAssignmentReview(assignmentId: string, score: number, code: string) {
  await wait(320)
  return mergeDynamicReview(assignmentId, score, code)
}

export async function getRecommendedProblems(
  assignmentId: string,
  score: number
): Promise<(ProblemBankEntry & { solved: boolean; reason: string })[]> {
  await wait(180)
  const state = useLmsStore.getState()
  const problem = codingProblems.find((item) => item.assignmentId === assignmentId)
  const assignment = assignments.find((item) => item.id === assignmentId)

  if (!problem || !assignment) {
    return []
  }

  const preferredDifficulty =
    score >= 85 ? problem.difficulty : score >= 70 ? "Medium" : "Easy"

  return state.problemBank
    .filter((entry) => entry.title !== problem.title)
    .filter(
      (entry) =>
        entry.recommendedForCourseIds.includes(assignment.courseId) ||
        entry.topics.some((topic) => problem.topics.includes(topic))
    )
    .sort((left, right) => {
      const leftMatchesDifficulty = left.difficulty === preferredDifficulty ? 1 : 0
      const rightMatchesDifficulty = right.difficulty === preferredDifficulty ? 1 : 0
      return rightMatchesDifficulty - leftMatchesDifficulty
    })
    .slice(0, 4)
    .map((entry) => ({
      ...entry,
      solved: entry.solvedByStudentIds.includes(studentProfile.id),
      reason:
        score >= 70
          ? "Recommended because you already passed the core tests and can stretch to the next pattern."
          : "Recommended to reinforce the same concept with a lower-friction practice set.",
    }))
}

export async function getLecturerOverview() {
  await wait(140)
  const managedCourseIds = lecturerManagedCourses.map((course) => course.id)
  const managedStudents = studentPerformance.filter((item) =>
    managedCourseIds.includes(item.courseId)
  )
  const submissions = useLmsStore
    .getState()
    .submissions.filter((submission) =>
      assignments.some(
        (assignment) =>
          assignment.id === submission.assignmentId &&
          managedCourseIds.includes(assignment.courseId)
      )
    )

  const pendingReviews = submissions.filter((submission) => submission.score < 80).length
  const averageScore =
    managedStudents.reduce((total, student) => total + student.averageScore, 0) /
    managedStudents.length

  return {
    managedCourses: lecturerManagedCourses.length,
    totalStudents: managedStudents.length,
    pendingReviews,
    averageScore: Math.round(averageScore),
  }
}

export async function getLecturerCourses() {
  await wait(120)
  return lecturerManagedCourses
}

export async function getLecturerCourseBundle(courseId: string) {
  await wait(180)
  const course = courses.find((item) => item.id === courseId)

  if (!course) {
    return null
  }

  const topics = await getStudentCourseTopics(courseId)
  const students = studentPerformance.filter((item) => item.courseId === courseId)
  const courseAssignments = assignments.filter((assignment) => assignment.courseId === courseId)

  return {
    course,
    topics,
    students,
    assignments: courseAssignments,
  }
}

export async function getProblemBankEntries() {
  await wait(120)
  return useLmsStore.getState().problemBank
}

export async function getStudentMonitoringRows(courseId: string): Promise<StudentPerformanceRecord[]> {
  await wait(120)
  return studentPerformance.filter((item) => item.courseId === courseId)
}

export function getAssignmentBundle(assignmentId: string) {
  const assignment = assignments.find((item) => item.id === assignmentId)
  const problem = codingProblems.find((item) => item.assignmentId === assignmentId)
  const latestSubmission = getLatestSubmission(assignmentId)
  const submissions = useLmsStore
    .getState()
    .submissions.filter((submission) => submission.assignmentId === assignmentId)

  return {
    assignment,
    problem,
    latestSubmission,
    submissions,
  }
}

export function getStudentCourseById(courseId: string): Course | undefined {
  return courses.find((item) => item.id === courseId)
}

export function getAssignmentOverview(assignmentId: string) {
  const { assignment, problem, latestSubmission, submissions } = getAssignmentBundle(assignmentId)

  if (!assignment || !problem) {
    return null
  }

  const bestScore = submissions.reduce(
    (highest, submission) => Math.max(highest, submission.score),
    0
  )

  return {
    assignment,
    problem,
    latestSubmission,
    submissions,
    bestScore,
    attemptsUsed: submissions.length,
    ...getAssignmentWindow(assignment),
  }
}
