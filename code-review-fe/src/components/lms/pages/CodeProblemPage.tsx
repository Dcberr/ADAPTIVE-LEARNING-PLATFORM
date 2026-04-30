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
import { ChevronLeft, ChevronRight, GripVertical, PanelLeftOpen, PanelRightOpen } from "lucide-react"

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
  getRecommendedProblems,
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
  type SubmissionDetailResponse,
  useCreateSubmissionMutation,
  useGetAssignmentContextQuery,
  useGetAssignmentProblemQuery,
  useGetAssignmentSubmissionsQuery,
  useGetAssignmentTestcasesQuery,
  useGetSubmissionByIdQuery,
  useJudgeExecutionMutation,
  useReviewCodeMutation,
} from "@/store/redux/api/lmsApi"
import { useToast } from "@/components/ui/toast-provider"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type Language = "cpp"
type ActiveTab = "description" | "testcases" | "result" | "review"
type DynamicTestcase = {
  input: string
  expectedOutput: string
  explanation: string
  hidden: boolean
}
type CollapsedPane = "none" | "left" | "right"

const DEFAULT_LEFT_PANE_WIDTH = 52
const MIN_LEFT_PANE_WIDTH = 28
const MAX_LEFT_PANE_WIDTH = 72

function toDifficultyLabel(value: string): "Easy" | "Medium" | "Hard" {
  if (value === "HARD") return "Hard"
  if (value === "MEDIUM") return "Medium"
  return "Easy"
}

function toSubmissionStatus(score: number): "submitted" | "reviewed" {
  return score >= 70 ? "reviewed" : "submitted"
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
    examples: visibleExamples,
    constraints: (assignmentProblem?.problemConstraint || cachedProblem?.problemConstraint)
      ? (assignmentProblem?.problemConstraint || cachedProblem?.problemConstraint)
          .split("\n")
          .map((item: string) => item.trim())
          .filter(Boolean)
      : [],
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
    eligibleForReview: percentage >= 70,
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

  return {
    passed,
    total,
    percentage,
    score: Math.round(((assignment.points || 100) * percentage) / 100),
    eligibleForReview: percentage >= 70,
    results: judgeResult.testcases.map((item: JudgeExecutionResponse["testcases"][number]) => ({
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
    eligibleForReview: percentage >= 70,
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
}: {
  id: string
  role?: "student" | "lecturer"
}) {
  const router = useRouter()
  const mockBundle = getAssignmentBundle(id)
  const hasMockBundle = Boolean(mockBundle.assignment && mockBundle.problem)
  const { data: assignmentContext, isLoading: isLoadingContext } = useGetAssignmentContextQuery(id, {
    skip: Boolean(mockBundle.assignment && mockBundle.problem),
  })
  const { data: assignmentProblem, isLoading: isLoadingProblem } = useGetAssignmentProblemQuery(id, {
    skip: Boolean(mockBundle.assignment && mockBundle.problem),
  })
  const { data: assignmentTestcases = [], isLoading: isLoadingTestcases } =
    useGetAssignmentTestcasesQuery(id, {
        skip: Boolean(mockBundle.assignment && mockBundle.problem),
    })
  const {
    data: backendSubmissionHistory = [],
  } = useGetAssignmentSubmissionsQuery(
    {
      assignmentId: id,
      scope: role === "student" ? "me" : "all",
    },
    { skip: hasMockBundle }
  )
  const [judgeExecution] = useJudgeExecutionMutation()
  const [reviewCode] = useReviewCodeMutation()
  const [createSubmission] = useCreateSubmissionMutation()
  const cachedProblem = useMemo(() => getCachedAssignmentProblem(id), [id])
  const assignment = useMemo(
    () => mockBundle.assignment ?? (assignmentContext ? buildDynamicAssignment(assignmentContext) : null),
    [assignmentContext, mockBundle.assignment]
  )
  const problem = useMemo(
    () =>
      mockBundle.problem ??
      (assignmentContext
        ? buildDynamicProblem(
            assignmentContext,
            assignmentProblem,
            assignmentTestcases,
            cachedProblem
          )
        : null),
    [assignmentContext, assignmentProblem, assignmentTestcases, cachedProblem, mockBundle.problem]
  )
  const [startedAtMs] = useState(() => Date.now())
  const language: Language = "cpp"
  const [code, setCode] = useState<string | null>(null)
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<ActiveTab>("description")
  const [execution, setExecution] = useState<ExecutionSummary | null>(null)
  const [review, setReview] = useState<CodeReviewFeedback | null>(null)
  const [recommendedProblems, setRecommendedProblems] = useState<
    Awaited<ReturnType<typeof getRecommendedProblems>>
  >([])
  const [runningAction, setRunningAction] = useState<"run" | "submit" | "review" | null>(null)
  const [collapsedPane, setCollapsedPane] = useState<CollapsedPane>("none")
  const [leftPaneWidth, setLeftPaneWidth] = useState(DEFAULT_LEFT_PANE_WIDTH)
  const [isDesktopLayout, setIsDesktopLayout] = useState(false)
  const { toast } = useToast()
  const submissions = useAppSelector((state) => state.lms.submissions)
  const workspaceRef = useRef<HTMLDivElement | null>(null)
  const dragStateRef = useRef<{ startX: number; startWidth: number } | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const timeLimitMinutes =
    assignmentContext?.timeLimit ??
    (assignment?.difficulty === "Hard" ? 60 : assignment?.difficulty === "Medium" ? 45 : 30)

  const submissionHistory = useMemo(
    () => submissions.filter((submission) => submission.assignmentId === id),
    [id, submissions]
  )
  const latestSubmission = submissionHistory[0] ?? mockBundle.latestSubmission
  const latestBackendSubmission = backendSubmissionHistory[0]
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
          eligibleForReview: latestSubmission.score >= 70,
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
      ? (latestSubmission?.score ?? 0) >= 70
      : Number(latestBackendSubmission?.score ?? 0) >= 70)
  const activeCode = code ?? (problem ? problem.functionSkeleton.cpp ?? "" : "")

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
      if (collapsedPane !== "none") {
        return
      }

      dragStateRef.current = {
        startX: event.clientX,
        startWidth: leftPaneWidth,
      }
      setIsDragging(true)
      event.preventDefault()
    },
    [collapsedPane, leftPaneWidth]
  )

  const expandSplitLayout = useCallback(() => {
    setCollapsedPane("none")
  }, [])

  const collapseLeftPane = useCallback(() => {
    setCollapsedPane("left")
  }, [])

  const collapseRightPane = useCallback(() => {
    setCollapsedPane("right")
  }, [])

  const loadReview = useCallback(async () => {
    if (!assignment) {
      return
    }

    const baseScore =
      displayedExecution?.score ??
      (hasMockBundle ? latestSubmission?.score : Number(latestBackendSubmission?.score ?? 0)) ??
      0

    if (!displayedExecution?.eligibleForReview && baseScore < 70) {
      handleTabChange("result")
      return
    }

    setRunningAction("review")

    try {
      const [reviewResult, recommendations] = await Promise.all([
        hasMockBundle
          ? getAssignmentReview(assignment.id, baseScore, activeCode)
          : !assignmentProblem?.id
            ? Promise.resolve(null)
            : reviewCode({
              problemId: assignmentProblem.id,
              code: activeCode,
              language,
            }).unwrap(),
        getRecommendedProblems(assignment.id, baseScore),
      ])

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
      setRecommendedProblems(recommendations)
      handleTabChange("review")
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
    assignmentProblem?.id,
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
        } else if (mode === "run" && assignmentProblem?.id) {
          try {
            const judgeResult = await judgeExecution({
              problemId: assignmentProblem.id,
              language,
              code: activeCode,
            }).unwrap()

            summary = mapJudgeExecutionToSummary(judgeResult, assignment, assignmentTestcases)
          } catch {
            summary = simulateDynamicExecution(assignment, problem!, activeCode, mode)
          }
        } else if (mode === "submit") {
          if (!assignmentProblem?.id) {
            throw new Error(
              "Thiếu problemId từ backend nên chưa thể gửi bài thật. Cần kiểm tra lại API /problems/assignment/{assignmentId}."
            )
          }

          const createdSubmission = await createSubmission({
            problemId: assignmentProblem.id,
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
              summary.eligibleForReview || (Number.isFinite(nextScore) ? nextScore >= 70 : false),
          })
          setReview(null)
          setRecommendedProblems([])
          handleTabChange("result")
          setRunningAction(null)
          toast({
            tone: "success",
            description: "Đã nộp bài thành công.",
          })
          router.push(`/${role}/assignments/${assignment.id}`)
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
        setRecommendedProblems([])
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
      assignment,
      assignmentProblem,
      assignmentTestcases,
      createSubmission,
      execution,
      fallbackExecution,
      getElapsedSeconds,
      handleTabChange,
      hasMockBundle,
      judgeExecution,
      language,
      problem,
      role,
      router,
      startedAtMs,
      toast,
    ]
  )

  if (isLoadingContext || isLoadingProblem || isLoadingTestcases) {
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
        backHref={`/${role}/assignments/${assignment.id}`}
        startedAtMs={startedAtMs}
        timeLimitMinutes={timeLimitMinutes}
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
            recommendedProblems={recommendedProblems}
            runningAction={runningAction}
            canRequestReview={canRequestReview}
            onLoadReview={loadReview}
          />

          <EditorWorkspaceCard
            language={language}
            code={activeCode}
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
          {collapsedPane !== "left" ? (
            <div
              className="relative min-w-0 shrink-0"
              style={{
                flexBasis: collapsedPane === "right" ? "100%" : `${leftPaneWidth}%`,
              }}
            >
              <div className="absolute right-4 top-4 z-10 flex items-center gap-2">
                {collapsedPane === "right" ? (
                  <Button
                    type="button"
                    size="icon"
                    variant="outline"
                    className="bg-white/95"
                    onClick={expandSplitLayout}
                    aria-label="Mở lại code editor"
                  >
                    <PanelRightOpen className="size-4" />
                  </Button>
                ) : (
                  <Button
                    type="button"
                    size="icon"
                    variant="outline"
                    className="bg-white/95"
                    onClick={collapseRightPane}
                    aria-label="Ẩn code editor"
                  >
                    <ChevronRight className="size-4" />
                  </Button>
                )}
              </div>
              <ProblemWorkspaceTabs
                problem={problem}
                activeTab={activeTab}
                onTabChange={handleTabChange}
                hasMounted={hasMounted}
                displayedExecution={displayedExecution}
                review={review}
                recommendedProblems={recommendedProblems}
                runningAction={runningAction}
                canRequestReview={canRequestReview}
                onLoadReview={loadReview}
              />
            </div>
          ) : null}

          {collapsedPane === "none" ? (
            <div
              role="separator"
              aria-orientation="vertical"
              aria-label="Resize workspace panels"
              className="group relative flex w-5 shrink-0 cursor-col-resize items-center justify-center"
              onPointerDown={handleDividerPointerDown}
            >
              <Button
                type="button"
                size="icon"
                variant="ghost"
                className="absolute left-1/2 top-4 z-10 size-8 -translate-x-1/2 rounded-full border border-slate-200 bg-white/95 text-slate-600 shadow-sm hover:bg-white"
                onClick={collapseLeftPane}
                aria-label="Ẩn panel bài tập"
              >
                <ChevronLeft className="size-4" />
              </Button>
              <div className="flex h-full w-full items-center justify-center">
                <div className="flex h-full w-[3px] items-center justify-center rounded-full bg-slate-200 transition group-hover:bg-[#1488D8]/50">
                  <GripVertical className="size-4 -translate-x-[6.5px] text-slate-400" />
                </div>
              </div>
            </div>
          ) : null}

          {collapsedPane !== "right" ? (
            <div
              className="relative min-w-0 shrink-0"
              style={{
                flexBasis: collapsedPane === "left" ? "100%" : `${100 - leftPaneWidth}%`,
              }}
            >
              <div className="absolute left-4 top-4 z-10 flex items-center gap-2">
                {collapsedPane === "left" ? (
                  <Button
                    type="button"
                    size="icon"
                    variant="outline"
                    className="bg-white/95"
                    onClick={expandSplitLayout}
                    aria-label="Mở lại panel bài tập"
                  >
                    <PanelLeftOpen className="size-4" />
                  </Button>
                ) : (
                  <Button
                    type="button"
                    size="icon"
                    variant="outline"
                    className="bg-white/95"
                    onClick={collapseLeftPane}
                    aria-label="Ẩn panel bài tập"
                  >
                    <ChevronLeft className="size-4" />
                  </Button>
                )}
              </div>
              <EditorWorkspaceCard
                language={language}
                code={activeCode}
                runningAction={runningAction}
                canRequestReview={canRequestReview}
                onCodeChange={setCode}
                onRun={() => handleExecute("run")}
                onSubmit={() => handleExecute("submit")}
                onReview={loadReview}
              />
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
