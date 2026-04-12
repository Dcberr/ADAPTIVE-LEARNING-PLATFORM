"use client"

import { useCallback, useMemo, useState } from "react"
import { useRouter } from "next/navigation"

import type { CodeReviewFeedback } from "@/data/lms/extendedMockData"
import SubmissionHistory from "@/components/lms/SubmissionHistory"
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
import { useGetAssignmentContextQuery } from "@/store/redux/api/lmsApi"

const mockLanguages = ["python", "javascript", "java", "cpp"] as const
const cppOnlyLanguages = ["cpp"] as const

type Language = (typeof mockLanguages)[number]
type ActiveTab = "description" | "testcases" | "result" | "review"

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
  cachedProblem: ReturnType<typeof getCachedAssignmentProblem>
): CodingProblem {
  const visibleExamples = (cachedProblem?.testcases ?? [])
    .filter((item) => !item.hidden)
    .slice(0, 2)
    .map((item) => ({
      input: item.input,
      output: item.expectedOutput,
      explanation: item.explanation,
    }))

  return {
    id: `problem-${context.id}`,
    assignmentId: context.id,
    title: context.title,
    difficulty: toDifficultyLabel(context.difficulty),
    description: cachedProblem?.description || "Đề bài đang được đồng bộ từ assignment này.",
    examples: visibleExamples,
    constraints: cachedProblem?.problemConstraint
      ? cachedProblem.problemConstraint.split("\n").map((item) => item.trim()).filter(Boolean)
      : [],
    starterCode: {
      python: "",
      javascript: "",
      java: "",
      cpp: cachedProblem?.starterCodeCpp ?? "",
    },
    testCases:
      cachedProblem?.testcases?.map((item) => ({
        input: item.input,
        expectedOutput: item.expectedOutput,
        hidden: item.hidden,
      })) ?? [],
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

export default function CodeProblemPage({
  id,
  role = "student",
}: {
  id: string
  role?: "student" | "lecturer"
}) {
  const router = useRouter()
  const mockBundle = getAssignmentBundle(id)
  const { data: assignmentContext, isLoading: isLoadingContext } = useGetAssignmentContextQuery(id, {
    skip: Boolean(mockBundle.assignment && mockBundle.problem),
  })
  const cachedProblem = useMemo(() => getCachedAssignmentProblem(id), [id])
  const hasMockBundle = Boolean(mockBundle.assignment && mockBundle.problem)
  const assignment = useMemo(
    () => mockBundle.assignment ?? (assignmentContext ? buildDynamicAssignment(assignmentContext) : null),
    [assignmentContext, mockBundle.assignment]
  )
  const problem = useMemo(
    () => mockBundle.problem ?? (assignmentContext ? buildDynamicProblem(assignmentContext, cachedProblem) : null),
    [assignmentContext, cachedProblem, mockBundle.problem]
  )
  const [startedAtMs] = useState(() => Date.now())
  const [language, setLanguage] = useState<Language>(hasMockBundle ? "python" : "cpp")
  const [code, setCode] = useState<string | null>(null)
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<ActiveTab>("description")
  const [execution, setExecution] = useState<ExecutionSummary | null>(null)
  const [review, setReview] = useState<CodeReviewFeedback | null>(null)
  const [recommendedProblems, setRecommendedProblems] = useState<
    Awaited<ReturnType<typeof getRecommendedProblems>>
  >([])
  const [runningAction, setRunningAction] = useState<"run" | "submit" | "review" | null>(null)
  const submissions = useAppSelector((state) => state.lms.submissions)
  const hasHydrated = useAppSelector((state) => state.lms.hasHydrated)
  const availableLanguages = hasMockBundle ? mockLanguages : cppOnlyLanguages
  const timeLimitMinutes =
    assignmentContext?.timeLimit ??
    (assignment?.difficulty === "Hard" ? 60 : assignment?.difficulty === "Medium" ? 45 : 30)

  const submissionHistory = useMemo(
    () => submissions.filter((submission) => submission.assignmentId === id),
    [id, submissions]
  )
  const latestSubmission = submissionHistory[0] ?? mockBundle.latestSubmission

  const fallbackExecution = useMemo(
    () =>
      latestSubmission
        ? {
            passed: latestSubmission.passed,
            total: latestSubmission.total,
            percentage: Math.round((latestSubmission.passed / latestSubmission.total) * 100),
            score: latestSubmission.score,
            results: latestSubmission.testResults,
            eligibleForReview: latestSubmission.score >= 70,
          }
        : null,
    [latestSubmission]
  )

  const displayedExecution = useMemo(
    () => execution ?? fallbackExecution,
    [execution, fallbackExecution]
  )
  const canRequestReview =
    (displayedExecution?.eligibleForReview ?? false) || (latestSubmission?.score ?? 0) >= 70
  const activeCode = code ?? (problem ? problem.starterCode[language] ?? "" : "")

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
      setCode(problem.starterCode[selectedLanguage] ?? "")
    },
    [problem]
  )

  const loadReview = useCallback(async () => {
    if (!assignment) {
      return
    }

    const baseScore = displayedExecution?.score ?? latestSubmission?.score ?? 0

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
    latestSubmission?.score,
    activeCode,
  ])

  const handleExecute = useCallback(
    async (mode: "run" | "submit") => {
      if (!assignment) {
        return
      }

      setRunningAction(mode)
      const summary = hasMockBundle
        ? await runAssignmentExecution(assignment.id, language, activeCode, mode, {
            startedAt: new Date(startedAtMs).toISOString(),
            durationSeconds: getElapsedSeconds(),
          })
        : simulateDynamicExecution(assignment, problem!, activeCode, mode)

      if (!hasMockBundle && mode === "submit") {
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
      handleTabChange("result")
      setRunningAction(null)

      if (mode === "submit") {
        router.push(`/${role}/assignments/${assignment.id}`)
      }
    },
    [activeCode, assignment, getElapsedSeconds, handleTabChange, hasMockBundle, language, problem, role, router, startedAtMs]
  )

  if (!assignment || !problem) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{isLoadingContext ? "Đang tải bài tập..." : "Không tìm thấy bài tập"}</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingContext ? "Hệ thống đang chuẩn bị dữ liệu cho màn làm bài." : "Assignment is unavailable."}
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

      {hasHydrated ? <SubmissionHistory submissions={submissionHistory} /> : null}
    </div>
  )
}
