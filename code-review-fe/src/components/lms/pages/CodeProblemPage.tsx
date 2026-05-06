"use client"

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
} from "react"
import { useRouter } from "next/navigation"
import { GripVertical } from "lucide-react"

import { AttemptWorkspaceSkeleton } from "@/components/lms/LmsLoadingStates"
import type { CodeReviewFeedback } from "@/data/lms/extendedMockData"
import AssignmentAttemptHeader from "@/components/lms/pages/code-problem/AssignmentAttemptHeader"
import EditorWorkspaceCard from "@/components/lms/pages/code-problem/EditorWorkspaceCard"
import ProblemWorkspaceTabs from "@/components/lms/pages/code-problem/ProblemWorkspaceTabs"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { getCachedAssignmentProblem } from "@/lib/assignment-problem-cache"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Assignment, CodingProblem } from "@/data/lms/mockData"
import {
  getAssignmentBundle,
  getAssignmentReview,
  runAssignmentExecution,
  type ExecutionSummary,
} from "@/services/lms/mockLmsService"
import { useAppSelector } from "@/store/redux/hooks"
import { useLmsStore } from "@/store/lmsStore"
import {
  type AssignmentSubmissionResponse,
  type AssignmentTestcaseResponse,
  type JudgeExecutionResponse,
  type CodeReviewResponse,
  type RecommendationResponse,
  type ProblemDetailResponse,
  type SubmissionDetailResponse,
  useCreateSubmissionMutation,
  useGetRecommendationRoadmapMutation,
  useGetAssignmentContextQuery,
  useGetAssignmentProblemQuery,
  useGetAssignmentSubmissionsQuery,
  useGetAssignmentTestcasesQuery,
  useGetProblemByIdQuery,
  useGetProblemSubmissionsQuery,
  useGetSubmissionByIdQuery,
  useJudgeExecutionMutation,
  useReviewCodeMutation,
} from "@/store/redux/api/lmsApi"
import { useToast } from "@/components/ui/toast-provider"
import { cn } from "@/lib/utils"

type Language = "cpp"
type ActiveTab = "description" | "testcases" | "result" | "review"
type DynamicTestcase = {
  input: string
  expectedOutput: string
  explanation: string
  hidden: boolean
}

const DEFAULT_LEFT_PANE_WIDTH = 50
const MIN_LEFT_PANE_WIDTH = 28
const MAX_LEFT_PANE_WIDTH = 72
const REVIEW_ELIGIBILITY_PERCENT = 30

function toDifficultyLabel(value: string): "Easy" | "Medium" | "Hard" {
  if (value === "HARD" || value === "Hard") return "Hard"
  if (value === "MEDIUM" || value === "Medium") return "Medium"
  return "Easy"
}

function toSubmissionStatus(score: number): "submitted" | "reviewed" {
  return score >= REVIEW_ELIGIBILITY_PERCENT ? "reviewed" : "submitted"
}

function buildDynamicAssignment(context: NonNullable<ReturnType<typeof useGetAssignmentContextQuery>["data"]>): Assignment {
  return {
    id: context.id,
    courseId: context.classId,
    courseName: context.className,
    courseColor: "bg-[#030391]",
    title: context.title,
    dueDate: context.deadline,
    status: "pending",
    points: context.maxScore ?? 100,
    difficulty: toDifficultyLabel(context.difficulty),
    type: "code",
  }
}

function buildDynamicProblem(
  context: NonNullable<ReturnType<typeof useGetAssignmentContextQuery>["data"]>,
  assignmentProblem: ReturnType<typeof useGetAssignmentProblemQuery>["data"],
  assignmentTestcases: ReturnType<typeof useGetAssignmentTestcasesQuery>["data"],
  cachedProblem: ReturnType<typeof getCachedAssignmentProblem>
): CodingProblem {
  const sourceTestcases: DynamicTestcase[] =
    assignmentTestcases && assignmentTestcases.length > 0
      ? assignmentTestcases
      : (cachedProblem?.testcases ?? [])
  const visibleExamples = sourceTestcases
    .filter((item) => !item.hidden)
    .slice(0, 2)
    .map((item) => ({
      input: item.input,
      output: item.expectedOutput,
      explanation: item.explanation,
    }))

  return {
    id: assignmentProblem?.id ?? `problem-${context.id}`,
    assignmentId: context.id,
    title: context.title,
    difficulty: toDifficultyLabel(context.difficulty),
    description:
      assignmentProblem?.description ||
      cachedProblem?.description ||
      "Đề bài đang được đồng bộ từ assignment này.",
    problemConstraint:
      assignmentProblem?.problemConstraint || cachedProblem?.problemConstraint || "",
    examples: visibleExamples,
    constraints: [],
    functionSkeleton: {
      python: "",
      javascript: "",
      java: "",
      cpp: assignmentProblem?.functionSkeletons?.cpp ?? cachedProblem?.functionSkeletonCpp ?? "",
    },
    testCases: sourceTestcases.map((item) => ({
      input: item.input,
      expectedOutput: item.expectedOutput,
      hidden: item.hidden,
    })),
    hints: [],
    topics: cachedProblem?.tags ?? context.tags ?? [],
  }
}

function buildPracticeAssignment(problem: ProblemDetailResponse): Assignment {
  return {
    id: problem.id,
    courseId: "problem-bank",
    courseName: "Problem Bank",
    courseColor: "bg-[#1488D8]",
    title: problem.title,
    dueDate: "",
    status: "pending",
    points: 100,
    difficulty: toDifficultyLabel(problem.difficulty),
    type: "code",
  }
}

function buildPracticeProblem(problem: ProblemDetailResponse): CodingProblem {
  const visibleExamples = (problem.testcases ?? [])
    .filter((item) => !item.hidden)
    .slice(0, 2)
    .map((item) => ({
      input: item.input,
      output: item.expectedOutput,
      explanation: item.explanation,
    }))

  return {
    id: problem.id,
    assignmentId: problem.id,
    title: problem.title,
    difficulty: toDifficultyLabel(problem.difficulty),
    description: problem.description || "Đề bài đang được đồng bộ từ thư viện bài luyện tập.",
    problemConstraint: problem.problemConstraint ?? "",
    examples: visibleExamples,
    constraints: [],
    functionSkeleton: {
      python: problem.functionSkeletons?.python ?? "",
      javascript: problem.functionSkeletons?.javascript ?? "",
      java: problem.functionSkeletons?.java ?? "",
      cpp: problem.functionSkeletons?.cpp ?? "",
    },
    testCases: (problem.testcases ?? []).map((item) => ({
      input: item.input,
      expectedOutput: item.expectedOutput,
      hidden: item.hidden,
    })),
    hints: [],
    topics: problem.tags ?? [],
  }
}

function simulateDynamicExecution(
  assignment: Assignment,
  problem: CodingProblem,
  code: string,
  mode: "run" | "submit"
): ExecutionSummary {
  const availableCases =
    mode === "run" ? problem.testCases.filter((item) => !item.hidden) : problem.testCases
  const safeCases =
    availableCases.length > 0
      ? availableCases
      : [{ input: "sample", expectedOutput: "sample", hidden: false }]
  const normalized = code.toLowerCase()
  let confidence = 0.2

  if (normalized.length > 80) confidence += 0.2
  if (/(return|cout|for|while)/.test(normalized)) confidence += 0.35
  if (!/todo|pass/.test(normalized)) confidence += 0.15

  const total = safeCases.length
  const passed = Math.max(1, Math.min(total, Math.round(confidence * total)))
  const percentage = Math.round((passed / total) * 100)
  const score = Math.round(((assignment.points || 100) * percentage) / 100)

  return {
    passed,
    total,
    percentage,
    score,
    eligibleForReview: percentage >= REVIEW_ELIGIBILITY_PERCENT,
    results: safeCases.map((testCase, index) => ({
      idx: index + 1,
      input: testCase.input,
      expected: testCase.expectedOutput,
      actual: index < passed ? testCase.expectedOutput : "Unexpected output",
      passed: index < passed,
      hidden: testCase.hidden,
    })),
  }
}

function mapJudgeExecutionToSummary(
  judgeResult: JudgeExecutionResponse,
  assignment: Assignment,
  assignmentTestcases: AssignmentTestcaseResponse[]
): ExecutionSummary {
  const total = judgeResult.totalTestcases || judgeResult.testcases.length
  const passed = judgeResult.passedTestcases
  const percentage = total > 0 ? Math.round((passed / total) * 100) : 0
  const testcaseVisibility = new Map(
    assignmentTestcases.map((item: AssignmentTestcaseResponse) => [item.id, item.hidden])
  )
  const hasCompileError = judgeResult.status === "COMPILE_ERROR"

  return {
    passed,
    total,
    percentage,
    score: Math.round(((assignment.points || 100) * percentage) / 100),
    eligibleForReview: percentage >= REVIEW_ELIGIBILITY_PERCENT,
    status: judgeResult.status,
    errorMessage: judgeResult.errorMessage ?? null,
    results: hasCompileError
      ? []
      : judgeResult.testcases.map((item: JudgeExecutionResponse["testcases"][number]) => ({
          idx: item.index,
          input: item.input,
          expected: item.expectedOutput,
          actual: item.output || item.error || "",
          passed: item.status === "ACCEPTED",
          hidden: item.testcaseId ? testcaseVisibility.get(item.testcaseId) ?? false : false,
        })),
  }
}

function mapSubmissionDetailToSummary(
  submission: AssignmentSubmissionResponse,
  detail: SubmissionDetailResponse
): ExecutionSummary {
  const total = detail.testcaseResults.length
  const passed = detail.testcaseResults.filter((item) => item.status === "ACCEPTED").length
  const percentage = total > 0 ? Math.round((passed / total) * 100) : 0
  const numericScore = Number(submission.score)

  return {
    passed,
    total,
    percentage,
    score: Number.isFinite(numericScore) ? numericScore : 0,
    eligibleForReview: percentage >= REVIEW_ELIGIBILITY_PERCENT,
    results: detail.testcaseResults.map((item) => ({
      idx: item.index,
      input: item.input,
      expected: item.expectedOutput,
      actual: item.output || item.error || "",
      passed: item.status === "ACCEPTED",
      hidden: false,
    })),
  }
}

function mapCodeReviewResponseToFeedback(
  assignmentId: string,
  response: CodeReviewResponse
): CodeReviewFeedback {
  const positiveItems = response.review_items.filter((item) => item.type.toLowerCase() === "info")
  const negativeItems = response.review_items.filter((item) => item.type.toLowerCase() !== "info")
  const strengths = positiveItems.map((item) => item.issue).filter(Boolean)
  const weaknesses = negativeItems.map((item) => item.issue).filter(Boolean)
  const improvements = response.review_items
    .map((item) => item.fix_suggestion)
    .filter((item): item is string => Boolean(item))

  return {
    assignmentId,
    strengths:
      strengths.length > 0
        ? strengths
        : response.summary
          ? [response.summary]
          : ["Bài nộp đã có đủ dữ liệu để hệ thống phân tích."],
    weaknesses:
      weaknesses.length > 0
        ? weaknesses
        : response.detail
          ? [response.detail]
          : [],
    improvements,
    summary: response.summary,
    detail: response.detail,
    reviewId: response.review_id,
    reviewItems: response.review_items.map((item) => ({
      line: item.line,
      column: item.column,
      type: item.type,
      issue: item.issue,
      codeSnippet: item.code_snippet,
      fixSuggestion: item.fix_suggestion,
      reviewLink: item.review_link
        ? {
            currentIssue: item.review_link.current_issue,
            currentCodeSnippet: item.review_link.current_code_snippet,
            previousSubmissionIndexes: item.review_link.previous_submission_indexes,
            previousCodeSnippet: item.review_link.previous_code_snippet,
            whatImproved: item.review_link.what_improved,
            whatStillNeedsWork: item.review_link.what_still_needs_work,
            relationSummary: item.review_link.relation_summary,
          }
        : null,
    })),
    scorecard: response.scorecard,
  }
}

export default function CodeProblemPage({
  id,
  role = "student",
  source = "assignment",
}: {
  id: string
  role?: "student" | "lecturer"
  source?: "assignment" | "practice"
}) {
  const router = useRouter()
  const isPractice = source === "practice"
  const mockBundle = !isPractice ? getAssignmentBundle(id) : { assignment: null, problem: null, latestSubmission: null }
  const hasMockBundle = !isPractice && Boolean(mockBundle.assignment && mockBundle.problem)
  const { data: assignmentContext, isLoading: isLoadingContext } = useGetAssignmentContextQuery(id, {
    skip: isPractice || Boolean(mockBundle.assignment && mockBundle.problem),
  })
  const { data: assignmentProblem, isLoading: isLoadingProblem } = useGetAssignmentProblemQuery(id, {
    skip: isPractice || Boolean(mockBundle.assignment && mockBundle.problem),
  })
  const { data: assignmentTestcases = [], isLoading: isLoadingTestcases } =
    useGetAssignmentTestcasesQuery(id, {
        skip: isPractice || Boolean(mockBundle.assignment && mockBundle.problem),
    })
  const { data: practiceProblem, isLoading: isLoadingPracticeProblem } = useGetProblemByIdQuery(id, {
    skip: !isPractice,
  })
  const {
    data: backendSubmissionHistory = [],
  } = useGetAssignmentSubmissionsQuery(
    {
      assignmentId: id,
      scope: role === "student" ? "me" : "all",
    },
    { skip: hasMockBundle || isPractice }
  )
  const { data: practiceSubmissionHistory = [] } = useGetProblemSubmissionsQuery(id, {
    skip: !isPractice,
  })
  const [judgeExecution] = useJudgeExecutionMutation()
  const [reviewCode] = useReviewCodeMutation()
  const [createSubmission] = useCreateSubmissionMutation()
  const cachedProblem = useMemo(() => getCachedAssignmentProblem(id), [id])
  const assignment = useMemo(
    () =>
      isPractice
        ? (practiceProblem ? buildPracticeAssignment(practiceProblem) : null)
        : mockBundle.assignment ?? (assignmentContext ? buildDynamicAssignment(assignmentContext) : null),
    [assignmentContext, isPractice, mockBundle.assignment, practiceProblem]
  )
  const problem = useMemo(
    () =>
      isPractice
        ? (practiceProblem ? buildPracticeProblem(practiceProblem) : null)
        : mockBundle.problem ??
          (assignmentContext
            ? buildDynamicProblem(
                assignmentContext,
                assignmentProblem,
                assignmentTestcases,
                cachedProblem
              )
            : null),
    [
      assignmentContext,
      assignmentProblem,
      assignmentTestcases,
      cachedProblem,
      isPractice,
      mockBundle.problem,
      practiceProblem,
    ]
  )
  const [startedAtMs] = useState(() => Date.now())
  const language: Language = "cpp"
  const [code, setCode] = useState<string | null>(null)
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<ActiveTab>("description")
  const [execution, setExecution] = useState<ExecutionSummary | null>(null)
  const [review, setReview] = useState<CodeReviewFeedback | null>(null)
  const [recommendationRoadmap, setRecommendationRoadmap] = useState<RecommendationResponse | null>(null)
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false)
  const [isRecommendationDialogOpen, setIsRecommendationDialogOpen] = useState(false)
  const [runningAction, setRunningAction] = useState<"run" | "submit" | "review" | null>(null)
  const [leftPaneWidth, setLeftPaneWidth] = useState(DEFAULT_LEFT_PANE_WIDTH)
  const [isDesktopLayout, setIsDesktopLayout] = useState(false)
  const { toast } = useToast()
  const submissions = useAppSelector((state) => state.lms.submissions)
  const currentUserId = useAppSelector((state) => state.auth.user?.id ?? "")
  const workspaceRef = useRef<HTMLDivElement | null>(null)
  const dragStateRef = useRef<{ startX: number; startWidth: number } | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [getRecommendationRoadmap] = useGetRecommendationRoadmapMutation()
  const timeLimitMinutes =
    isPractice
      ? 0
      : assignmentContext?.timeLimit ??
        (assignment?.difficulty === "Hard" ? 60 : assignment?.difficulty === "Medium" ? 45 : 30)

  const submissionHistory = useMemo(
    () => submissions.filter((submission) => submission.assignmentId === id),
    [id, submissions]
  )
  const latestSubmission = submissionHistory[0] ?? mockBundle.latestSubmission
  const latestBackendSubmission = isPractice ? practiceSubmissionHistory[0] : backendSubmissionHistory[0]
  const { data: latestBackendSubmissionDetail } = useGetSubmissionByIdQuery(
    latestBackendSubmission?.submissionId ?? "",
    {
      skip: hasMockBundle || !latestBackendSubmission?.submissionId,
    }
  )

  const fallbackExecution = useMemo(
    () => {
      if (hasMockBundle && latestSubmission) {
        return {
          passed: latestSubmission.passed,
          total: latestSubmission.total,
          percentage: Math.round((latestSubmission.passed / latestSubmission.total) * 100),
          score: latestSubmission.score,
          results: latestSubmission.testResults,
          eligibleForReview: latestSubmission.score >= REVIEW_ELIGIBILITY_PERCENT,
        }
      }

      if (!hasMockBundle && latestBackendSubmission && latestBackendSubmissionDetail) {
        return mapSubmissionDetailToSummary(latestBackendSubmission, latestBackendSubmissionDetail)
      }

      return null
    },
    [hasMockBundle, latestBackendSubmission, latestBackendSubmissionDetail, latestSubmission]
  )

  const displayedExecution = useMemo(
    () => execution ?? fallbackExecution,
    [execution, fallbackExecution]
  )
  const canRequestReview =
    (displayedExecution?.eligibleForReview ?? false) ||
    (hasMockBundle
      ? (latestSubmission?.score ?? 0) >= REVIEW_ELIGIBILITY_PERCENT
      : Number(latestBackendSubmission?.score ?? 0) >= REVIEW_ELIGIBILITY_PERCENT)
  const activeCode = code ?? (problem ? problem.functionSkeleton.cpp ?? "" : "")
  const activeProblemId = problem?.id ?? null

  const getElapsedSeconds = useCallback(
    () => Math.floor((Date.now() - startedAtMs) / 1000),
    [startedAtMs]
  )

  useEffect(() => {
    const mediaQuery = window.matchMedia("(min-width: 1280px)")
    const syncLayoutMode = () => setIsDesktopLayout(mediaQuery.matches)

    syncLayoutMode()
    mediaQuery.addEventListener("change", syncLayoutMode)

    return () => {
      mediaQuery.removeEventListener("change", syncLayoutMode)
    }
  }, [])

  useEffect(() => {
    if (!isDragging) {
      return
    }

    const handlePointerMove = (event: PointerEvent) => {
      const container = workspaceRef.current
      const dragState = dragStateRef.current

      if (!container || !dragState) {
        return
      }

      const containerWidth = container.getBoundingClientRect().width

      if (containerWidth <= 0) {
        return
      }

      const deltaPercent = ((event.clientX - dragState.startX) / containerWidth) * 100
      const nextWidth = Math.min(
        MAX_LEFT_PANE_WIDTH,
        Math.max(MIN_LEFT_PANE_WIDTH, dragState.startWidth + deltaPercent)
      )

      setLeftPaneWidth(nextWidth)
    }

    const handlePointerUp = () => {
      dragStateRef.current = null
      setIsDragging(false)
    }

    const previousCursor = document.body.style.cursor
    const previousUserSelect = document.body.style.userSelect
    document.body.style.cursor = "col-resize"
    document.body.style.userSelect = "none"

    window.addEventListener("pointermove", handlePointerMove)
    window.addEventListener("pointerup", handlePointerUp)

    return () => {
      document.body.style.cursor = previousCursor
      document.body.style.userSelect = previousUserSelect
      window.removeEventListener("pointermove", handlePointerMove)
      window.removeEventListener("pointerup", handlePointerUp)
    }
  }, [isDragging])

  const handleDividerPointerDown = useCallback(
    (event: ReactPointerEvent<HTMLDivElement>) => {
      dragStateRef.current = {
        startX: event.clientX,
        startWidth: leftPaneWidth,
      }
      setIsDragging(true)
      event.preventDefault()
    },
    [leftPaneWidth]
  )

  const loadReview = useCallback(async () => {
    if (!assignment) {
      return
    }

    const baseScore =
      displayedExecution?.score ??
      (hasMockBundle ? latestSubmission?.score : Number(latestBackendSubmission?.score ?? 0)) ??
      0

    if (!displayedExecution?.eligibleForReview && baseScore < REVIEW_ELIGIBILITY_PERCENT) {
      handleTabChange("result")
      return
    }

    handleTabChange("review")
    setRunningAction("review")
    setReview(null)
    setRecommendationRoadmap(null)
    setIsRecommendationDialogOpen(false)
    setIsRecommendationLoading(false)

    try {
      const reviewResult =
        hasMockBundle
          ? await getAssignmentReview(assignment.id, baseScore, activeCode)
          : !activeProblemId
            ? null
            : await reviewCode({
                problemId: activeProblemId,
                code: activeCode,
                language,
              }).unwrap()

      let nextReview: CodeReviewFeedback

      if (hasMockBundle) {
        nextReview = reviewResult as CodeReviewFeedback
      } else if (reviewResult) {
        nextReview = mapCodeReviewResponseToFeedback(
          assignment.id,
          reviewResult as CodeReviewResponse
        )
      } else {
        nextReview = {
          assignmentId: assignment.id,
          strengths: ["Backend review chưa khả dụng cho bài demo."],
          weaknesses: [],
          improvements: ["Dùng assignment thật để xem AI review từ backend."],
        }
      }

      setReview(nextReview)
    } catch (error) {
      toast({
        tone: "error",
        description: error instanceof Error ? error.message : "Không thể lấy AI review từ backend.",
      })
      handleTabChange("result")
    } finally {
      setRunningAction(null)
    }
  }, [
    assignment,
    activeProblemId,
    displayedExecution?.eligibleForReview,
    displayedExecution?.score,
    handleTabChange,
    hasMockBundle,
    latestSubmission?.score,
    latestBackendSubmission?.score,
    activeCode,
    language,
    reviewCode,
    toast,
  ])

  const loadRecommendationRoadmap = useCallback(async () => {
    if (!activeProblemId || !currentUserId) {
      setRecommendationRoadmap(null)
      return
    }

    setIsRecommendationLoading(true)

    try {
      const roadmap = await getRecommendationRoadmap({
        student_id: currentUserId,
        current_exercise_id: activeProblemId,
      }).unwrap()
      setRecommendationRoadmap(roadmap)
    } catch (error) {
      setRecommendationRoadmap(null)
      toast({
        tone: "error",
        description:
          error instanceof Error
            ? error.message
            : "Không thể tải gợi ý bài tập tiếp theo.",
      })
    } finally {
      setIsRecommendationLoading(false)
    }
  }, [activeProblemId, currentUserId, getRecommendationRoadmap, toast])

  const handleRecommendationDialogOpenChange = useCallback(
    (open: boolean) => {
      setIsRecommendationDialogOpen(open)

      if (open && !recommendationRoadmap && !isRecommendationLoading) {
        void loadRecommendationRoadmap()
      }
    },
    [isRecommendationLoading, loadRecommendationRoadmap, recommendationRoadmap]
  )

  const handleExecute = useCallback(
    async (mode: "run" | "submit") => {
      if (!assignment) {
        return
      }

      setRunningAction(mode)
      let summary: ExecutionSummary

      try {
        if (hasMockBundle) {
          summary = await runAssignmentExecution(assignment.id, language, activeCode, mode, {
            startedAt: new Date(startedAtMs).toISOString(),
            durationSeconds: getElapsedSeconds(),
          })
        } else if (mode === "run" && activeProblemId) {
          try {
            const judgeResult = await judgeExecution({
              problemId: activeProblemId,
              language,
              code: activeCode,
            }).unwrap()

            summary = mapJudgeExecutionToSummary(judgeResult, assignment, assignmentTestcases)
          } catch {
            summary = simulateDynamicExecution(assignment, problem!, activeCode, mode)
          }
        } else if (mode === "submit") {
          const targetProblemId = activeProblemId

          if (!targetProblemId) {
            throw new Error(
              isPractice
                ? "Thiếu problemId từ backend nên chưa thể nộp bài luyện tập. Cần kiểm tra lại API /problems/{problemId}."
                : "Thiếu problemId từ backend nên chưa thể gửi bài thật. Cần kiểm tra lại API /problems/assignment/{assignmentId}."
            )
          }

          const createdSubmission = await createSubmission({
            problemId: targetProblemId,
            language,
            code: activeCode,
            startedAt: new Date(startedAtMs).toISOString(),
          }).unwrap()
          const nextScore = Number(createdSubmission.score)

          summary =
            execution ??
            fallbackExecution ??
            simulateDynamicExecution(assignment, problem!, activeCode, mode)

          setExecution({
            ...summary,
            score: Number.isFinite(nextScore) ? nextScore : summary.score,
            eligibleForReview:
              summary.eligibleForReview ||
              (Number.isFinite(nextScore)
                ? nextScore >= REVIEW_ELIGIBILITY_PERCENT
                : false),
          })
          setReview(null)
          setRecommendationRoadmap(null)
          setIsRecommendationDialogOpen(false)
          setIsRecommendationLoading(false)
          handleTabChange("result")
          setRunningAction(null)
          toast({
            tone: "success",
            description: isPractice ? "Đã lưu lần nộp vào lịch sử luyện tập." : "Đã nộp bài thành công.",
          })
          router.push(
            isPractice ? `/${role}/problem-bank/${targetProblemId}` : `/${role}/assignments/${assignment.id}`
          )
          return
        } else {
          summary = simulateDynamicExecution(assignment, problem!, activeCode, mode)
        }

        if (hasMockBundle && mode === "submit") {
          useLmsStore.getState().addSubmission({
            id: `submission-${Date.now()}`,
            assignmentId: assignment.id,
            startedAt: new Date(startedAtMs).toISOString(),
            submittedAt: new Date().toISOString(),
            finishedAt: new Date().toISOString(),
            durationSeconds: getElapsedSeconds(),
            language,
            score: summary.score,
            passed: summary.passed,
            total: summary.total,
            status: toSubmissionStatus(summary.score),
            code: activeCode,
            testResults: summary.results,
          })
        }

        setExecution(summary)
        setReview(null)
        setRecommendationRoadmap(null)
        setIsRecommendationDialogOpen(false)
        setIsRecommendationLoading(false)
        handleTabChange("result")
      } catch (error) {
        toast({
          tone: "error",
          description: error instanceof Error ? error.message : "Không thể thực hiện thao tác này.",
        })
      } finally {
        setRunningAction(null)
      }
    },
    [
      activeCode,
      activeProblemId,
      assignment,
      assignmentTestcases,
      createSubmission,
      execution,
      fallbackExecution,
      getElapsedSeconds,
      handleTabChange,
      hasMockBundle,
      isPractice,
      judgeExecution,
      language,
      problem,
      role,
      router,
      startedAtMs,
      toast,
    ]
  )

  if (
    (!isPractice && (isLoadingContext || isLoadingProblem || isLoadingTestcases)) ||
    (isPractice && isLoadingPracticeProblem)
  ) {
    return <AttemptWorkspaceSkeleton title="Hệ thống đang chuẩn bị dữ liệu cho màn làm bài." />
  }

  if (!assignment || !problem) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Không tìm thấy bài tập</CardTitle>
        </CardHeader>
        <CardContent>Assignment is unavailable.</CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <AssignmentAttemptHeader
        assignment={assignment}
        problem={problem}
        backHref={isPractice ? `/${role}/problem-bank/${problem.id}` : `/${role}/assignments/${assignment.id}`}
        startedAtMs={startedAtMs}
        timeLimitMinutes={timeLimitMinutes}
        timerLabel={isPractice ? "Không giới hạn thời gian" : undefined}
        language={language}
      />

      {!isDesktopLayout ? (
        <div className="grid gap-4">
          <ProblemWorkspaceTabs
            problem={problem}
            activeTab={activeTab}
            onTabChange={handleTabChange}
            hasMounted={hasMounted}
            displayedExecution={displayedExecution}
            review={review}
            recommendationRoadmap={recommendationRoadmap}
            role={role}
            isRecommendationLoading={isRecommendationLoading}
            isRecommendationDialogOpen={isRecommendationDialogOpen}
            runningAction={runningAction}
            canRequestReview={canRequestReview}
            onLoadReview={loadReview}
            onRecommendationDialogOpenChange={handleRecommendationDialogOpenChange}
            showExamplesSection={false}
          />

          <EditorWorkspaceCard
            language={language}
            code={activeCode}
            review={review}
            runningAction={runningAction}
            canRequestReview={canRequestReview}
            onCodeChange={setCode}
            onRun={() => handleExecute("run")}
            onSubmit={() => handleExecute("submit")}
            onReview={loadReview}
          />
        </div>
      ) : null}

      {isDesktopLayout ? (
        <div
          ref={workspaceRef}
          className={cn(
            "hidden min-h-[640px] xl:flex xl:items-stretch",
            isDragging ? "xl:cursor-col-resize" : ""
          )}
        >
          <div
            className="relative min-w-0 shrink-0"
            style={{
              flexBasis: `${leftPaneWidth}%`,
            }}
          >
            <ProblemWorkspaceTabs
              problem={problem}
              activeTab={activeTab}
              onTabChange={handleTabChange}
              hasMounted={hasMounted}
              displayedExecution={displayedExecution}
              review={review}
              recommendationRoadmap={recommendationRoadmap}
              role={role}
              isRecommendationLoading={isRecommendationLoading}
              isRecommendationDialogOpen={isRecommendationDialogOpen}
              runningAction={runningAction}
              canRequestReview={canRequestReview}
              onLoadReview={loadReview}
              onRecommendationDialogOpenChange={handleRecommendationDialogOpenChange}
              showExamplesSection={false}
            />
          </div>

          <div
            role="separator"
            aria-orientation="vertical"
            aria-label="Resize workspace panels"
            className="group flex w-5 shrink-0 cursor-col-resize items-center justify-center"
            onPointerDown={handleDividerPointerDown}
          >
            <div className="flex h-full w-full items-center justify-center">
              <div className="flex h-full w-[3px] items-center justify-center rounded-full bg-slate-200 transition group-hover:bg-[#1488D8]/50">
                <GripVertical className="size-4 -translate-x-[6.5px] text-slate-400" />
              </div>
            </div>
          </div>

          <div
            className="relative min-w-0 shrink-0"
            style={{
              flexBasis: `${100 - leftPaneWidth}%`,
            }}
          >
            <EditorWorkspaceCard
              language={language}
              code={activeCode}
              review={review}
              runningAction={runningAction}
              canRequestReview={canRequestReview}
              onCodeChange={setCode}
              onRun={() => handleExecute("run")}
              onSubmit={() => handleExecute("submit")}
              onReview={loadReview}
            />
          </div>
        </div>
      ) : null}
    </div>
  )
}
