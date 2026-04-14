"use client"

import { useCallback, useMemo, useState } from "react"
import { useRouter } from "next/navigation"

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
  type SubmissionDetailResponse,
  useCreateSubmissionMutation,
  useGetAssignmentContextQuery,
  useGetAssignmentProblemQuery,
  useGetAssignmentSubmissionsQuery,
  useGetAssignmentTestcasesQuery,
  useGetSubmissionByIdQuery,
  useJudgeExecutionMutation,
} from "@/store/redux/api/lmsApi"

const mockLanguages = ["python", "javascript", "java", "cpp"] as const
const cppOnlyLanguages = ["cpp"] as const

type Language = (typeof mockLanguages)[number]
type ActiveTab = "description" | "testcases" | "result" | "review"
type DynamicTestcase = {
  input: string
  expectedOutput: string
  explanation: string
  hidden: boolean
}

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
  const [language, setLanguage] = useState<Language>(hasMockBundle ? "python" : "cpp")
  const [code, setCode] = useState<string | null>(null)
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<ActiveTab>("description")
  const [execution, setExecution] = useState<ExecutionSummary | null>(null)
  const [review, setReview] = useState<CodeReviewFeedback | null>(null)
  const [actionFeedback, setActionFeedback] = useState<string | null>(null)
  const [recommendedProblems, setRecommendedProblems] = useState<
    Awaited<ReturnType<typeof getRecommendedProblems>>
  >([])
  const [runningAction, setRunningAction] = useState<"run" | "submit" | "review" | null>(null)
  const submissions = useAppSelector((state) => state.lms.submissions)
  const availableLanguages = hasMockBundle ? mockLanguages : cppOnlyLanguages
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
  const activeCode = code ?? (problem ? problem.functionSkeleton[language] ?? "" : "")

  const getElapsedSeconds = useCallback(
    () => Math.floor((Date.now() - startedAtMs) / 1000),
    [startedAtMs]
  )

  const handleLanguageChange = useCallback(
    (nextLanguage: string) => {
      if (!problem) {
        return
      }

      const selectedLanguage = nextLanguage as Language
      setLanguage(selectedLanguage)
      setCode(problem.functionSkeleton[selectedLanguage] ?? "")
    },
    [problem]
  )

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

    const [reviewResult, recommendations] = await Promise.all([
      getAssignmentReview(assignment.id, baseScore, activeCode),
      getRecommendedProblems(assignment.id, baseScore),
    ])

    setReview(reviewResult)
    setRecommendedProblems(recommendations)
    handleTabChange("review")
    setRunningAction(null)
  }, [
    assignment,
    displayedExecution?.eligibleForReview,
    displayedExecution?.score,
    handleTabChange,
    hasMockBundle,
    latestSubmission?.score,
    latestBackendSubmission?.score,
    activeCode,
  ])

  const handleExecute = useCallback(
    async (mode: "run" | "submit") => {
      if (!assignment) {
        return
      }

      setRunningAction(mode)
      setActionFeedback(null)
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
        setActionFeedback(error instanceof Error ? error.message : "Không thể thực hiện thao tác này.")
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
    ]
  )

  if (!assignment || !problem) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>
            {isLoadingContext || isLoadingProblem || isLoadingTestcases
              ? "Đang tải bài tập..."
              : "Không tìm thấy bài tập"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingContext || isLoadingProblem || isLoadingTestcases
            ? "Hệ thống đang chuẩn bị dữ liệu cho màn làm bài."
            : "Assignment is unavailable."}
        </CardContent>
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
        languages={availableLanguages}
        onLanguageChange={handleLanguageChange}
      />

      <div className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
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

      {actionFeedback ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {actionFeedback}
        </div>
      ) : null}
    </div>
  )
}
