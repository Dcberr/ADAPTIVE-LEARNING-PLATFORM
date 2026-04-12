"use client"

import { useCallback, useMemo, useState } from "react"
import { useRouter } from "next/navigation"

import type { CodeReviewFeedback } from "@/data/lms/extendedMockData"
import SubmissionHistory from "@/components/lms/SubmissionHistory"
import AssignmentAttemptHeader from "@/components/lms/pages/code-problem/AssignmentAttemptHeader"
import EditorWorkspaceCard from "@/components/lms/pages/code-problem/EditorWorkspaceCard"
import ProblemWorkspaceTabs from "@/components/lms/pages/code-problem/ProblemWorkspaceTabs"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  getAssignmentBundle,
  getAssignmentReview,
  getRecommendedProblems,
  runAssignmentExecution,
  type ExecutionSummary,
} from "@/services/lms/mockLmsService"
import { useAppSelector } from "@/store/redux/hooks"

const languages = ["python", "javascript", "java", "cpp"] as const

type Language = (typeof languages)[number]
type ActiveTab = "description" | "testcases" | "result" | "review"

export default function CodeProblemPage({ id }: { id: string }) {
  const router = useRouter()
  const { assignment, problem, latestSubmission } = getAssignmentBundle(id)
  const [startedAtMs] = useState(() => Date.now())
  const [language, setLanguage] = useState<Language>("python")
  const [code, setCode] = useState(problem?.starterCode.python ?? "")
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<ActiveTab>("description")
  const [execution, setExecution] = useState<ExecutionSummary | null>(null)
  const [review, setReview] = useState<CodeReviewFeedback | null>(null)
  const [recommendedProblems, setRecommendedProblems] = useState<
    Awaited<ReturnType<typeof getRecommendedProblems>>
  >([])
  const [runningAction, setRunningAction] = useState<"run" | "submit" | "review" | null>(null)
  const submissions = useAppSelector((state) => state.lms.submissions)
  const hasHydrated = useAppSelector((state) => state.lms.hasHydrated)
  const timeLimitMinutes =
    assignment?.difficulty === "Hard" ? 60 : assignment?.difficulty === "Medium" ? 45 : 30

  const submissionHistory = useMemo(
    () => submissions.filter((submission) => submission.assignmentId === id),
    [id, submissions]
  )

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
      setCode(problem.starterCode[selectedLanguage])
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
      getAssignmentReview(assignment.id, baseScore, code),
      getRecommendedProblems(assignment.id, baseScore),
    ])

    setReview(reviewResult)
    setRecommendedProblems(recommendations)
    handleTabChange("review")
    setRunningAction(null)
  }, [
    assignment,
    code,
    displayedExecution?.eligibleForReview,
    displayedExecution?.score,
    handleTabChange,
    latestSubmission?.score,
  ])

  const handleExecute = useCallback(
    async (mode: "run" | "submit") => {
      if (!assignment) {
        return
      }

      setRunningAction(mode)
      const summary = await runAssignmentExecution(assignment.id, language, code, mode, {
        startedAt: new Date(startedAtMs).toISOString(),
        durationSeconds: getElapsedSeconds(),
      })
      setExecution(summary)
      handleTabChange("result")
      setRunningAction(null)

      if (mode === "submit") {
        router.push(`/student/assignments/${assignment.id}`)
      }
    },
    [assignment, code, getElapsedSeconds, handleTabChange, language, router, startedAtMs]
  )

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
        assignmentId={assignment.id}
        assignment={assignment}
        problem={problem}
        startedAtMs={startedAtMs}
        timeLimitMinutes={timeLimitMinutes}
        language={language}
        languages={languages}
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
          code={code}
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
