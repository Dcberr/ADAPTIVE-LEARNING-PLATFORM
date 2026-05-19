"use client"

import { useCallback, useMemo, useState } from "react"

import { AttemptWorkspaceSkeleton } from "@/components/lms/LmsLoadingStates"
import type { UserRole } from "@/data/lms/extendedMockData"
import AssignmentAttemptHeader from "@/components/lms/pages/code-problem/AssignmentAttemptHeader"
import EditorWorkspaceCard from "@/components/lms/pages/code-problem/EditorWorkspaceCard"
import ProblemWorkspaceTabs from "@/components/lms/pages/code-problem/ProblemWorkspaceTabs"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Assignment, CodingProblem } from "@/data/lms/mockData"
import type { ExecutionSummary } from "@/services/lms/mockLmsService"
import { useAppSelector } from "@/store/redux/hooks"
import {
  type AssignmentContext,
  type AssignmentProblemResponse,
  type AssignmentSubmissionResponse,
  type AssignmentTestcaseResponse,
  type CodeReviewResponse,
  type RecommendationResponse,
  type SubmissionDetailResponse,
  useGetAssignmentContextQuery,
  useGetAssignmentProblemQuery,
  useGetRecommendationRoadmapMutation,
  useGetRecommendationHistoryBySubmissionQuery,
  useGetAssignmentSubmissionsQuery,
  useGetAssignmentTestcasesQuery,
  useGetSubmissionReviewsQuery,
  useGetSubmissionByIdQuery,
  useReviewSubmissionMutation,
} from "@/store/redux/api/lmsApi"
import { useToast } from "@/components/ui/toast-provider"

type ActiveTab = "description" | "testcases" | "result" | "review"

function toDifficultyLabel(value: string): "Easy" | "Medium" | "Hard" {
  if (value === "HARD") return "Hard"
  if (value === "MEDIUM") return "Medium"
  return "Easy"
}

function buildReviewAssignment(context: AssignmentContext): Assignment {
  return {
    id: context.id,
    courseId: context.classId,
    courseName: context.className,
    courseColor: "bg-[#030391]",
    title: context.title,
    dueDate: context.deadline,
    status: "submitted",
    points: context.maxScore ?? 100,
    difficulty: toDifficultyLabel(context.difficulty),
    type: "code",
  }
}

function buildReviewProblem(
  context: AssignmentContext,
  assignmentProblem?: AssignmentProblemResponse,
  assignmentTestcases: AssignmentTestcaseResponse[] = []
): CodingProblem {
  const visibleExamples = assignmentTestcases
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
    description: assignmentProblem?.description || "Đề bài đang được đồng bộ từ assignment này.",
    problemConstraint: assignmentProblem?.problemConstraint ?? "",
    examples: visibleExamples,
    constraints: [],
    functionSkeleton: {
      python: assignmentProblem?.functionSkeletons?.python ?? "",
      javascript: assignmentProblem?.functionSkeletons?.javascript ?? "",
      java: assignmentProblem?.functionSkeletons?.java ?? "",
      cpp: assignmentProblem?.functionSkeletons?.cpp ?? "",
    },
    testCases: assignmentTestcases.map((item) => ({
      input: item.input,
      expectedOutput: item.expectedOutput,
      hidden: item.hidden,
    })),
    hints: [],
    topics: context.tags ?? [],
  }
}

function mapSubmissionDetailToExecution(
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
    eligibleForReview: true,
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
) {
  const positiveItems = response.review_items.filter((item) => item.type.toLowerCase() === "info")
  const negativeItems = response.review_items.filter((item) => item.type.toLowerCase() !== "info")

  return {
    assignmentId,
    strengths: positiveItems.map((item) => item.issue).filter(Boolean),
    weaknesses: negativeItems.map((item) => item.issue).filter(Boolean),
    improvements: response.review_items
      .map((item) => item.fix_suggestion)
      .filter((item): item is string => Boolean(item)),
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
        : undefined,
    })),
  }
}

export default function SubmissionReviewPage({
  assignmentId,
  submissionId,
  role,
}: {
  assignmentId: string
  submissionId: string
  role: UserRole
}) {
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<ActiveTab>("description")
  const currentUserId = useAppSelector((state) => state.auth.user?.id ?? "")
  const [isRecommendationDialogOpen, setIsRecommendationDialogOpen] = useState(false)
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false)
  const [runningAction, setRunningAction] = useState<"review" | null>(null)
  const [manualReview, setManualReview] = useState<ReturnType<typeof mapCodeReviewResponseToFeedback> | null>(null)
  const [recommendationRoadmap, setRecommendationRoadmap] = useState<RecommendationResponse | null>(null)
  const [reviewSubmission] = useReviewSubmissionMutation()
  const [getRecommendationRoadmap] = useGetRecommendationRoadmapMutation()
  const { toast } = useToast()
  const { data: assignmentContext, isLoading: isLoadingAssignment, error: assignmentError } =
    useGetAssignmentContextQuery(assignmentId)
  const {
    data: submissions = [],
    isLoading: isLoadingSubmissions,
  } = useGetAssignmentSubmissionsQuery({
    assignmentId,
    scope: role === "student" ? "me" : "all",
  })
  const {
    data: assignmentProblem,
    isLoading: isLoadingProblem,
  } = useGetAssignmentProblemQuery(assignmentId)
  const {
    data: assignmentTestcases = [],
    isLoading: isLoadingTestcases,
  } = useGetAssignmentTestcasesQuery(assignmentId)
  const { data: submissionDetail, isLoading: isLoadingDetail, error: detailError } =
    useGetSubmissionByIdQuery(submissionId)
  const shouldLoadReviewHistory = Boolean(submissionDetail?.isReviewed) && Boolean(submissionId)
  const shouldLoadRecommendationHistory = Boolean(submissionDetail?.isRecommend) && Boolean(submissionId)
  const { data: reviewHistory = [], isLoading: isLoadingReviewHistory } = useGetSubmissionReviewsQuery(
    submissionId,
    {
      skip: !shouldLoadReviewHistory,
    }
  )
  const { data: recommendationHistory = [], isLoading: isLoadingRecommendationHistory } =
    useGetRecommendationHistoryBySubmissionQuery(submissionId, {
      skip: !shouldLoadRecommendationHistory,
    })
  const submission = submissions.find((item) => item.submissionId === submissionId)
  const assignment = useMemo(
    () => (assignmentContext ? buildReviewAssignment(assignmentContext) : null),
    [assignmentContext]
  )
  const problem = useMemo(
    () =>
      assignmentContext
        ? buildReviewProblem(assignmentContext, assignmentProblem, assignmentTestcases)
        : null,
    [assignmentContext, assignmentProblem, assignmentTestcases]
  )
  const execution = useMemo(
    () =>
      submission && submissionDetail ? mapSubmissionDetailToExecution(submission, submissionDetail) : null,
    [submission, submissionDetail]
  )
  const latestHistoricalReview = useMemo(
    () =>
      reviewHistory.length > 0
        ? mapCodeReviewResponseToFeedback(assignmentId, reviewHistory[0])
        : null,
    [assignmentId, reviewHistory]
  )
  const latestHistoricalRecommendation = useMemo<RecommendationResponse | null>(
    () =>
      recommendationHistory.length > 0
        ? recommendationHistory[0].recommendation
        : null,
    [recommendationHistory]
  )
  const review = manualReview ?? latestHistoricalReview
  const activeRecommendationRoadmap = recommendationRoadmap ?? latestHistoricalRecommendation
  const code = submissionDetail?.code ?? ""
  const language = submissionDetail?.language ?? "cpp"
  const backHref = `/${role}/assignments/${assignmentId}`
  const startedAtMs = submission?.startedAt ? new Date(submission.startedAt).getTime() : 0

  const loadReview = useCallback(async () => {
    if (submissionDetail?.isReviewed && latestHistoricalReview) {
      handleTabChange("review")
      return
    }

    if (!assignmentProblem?.id || !code) {
      return
    }

    handleTabChange("review")
    setRunningAction("review")

    try {
      const reviewResult = await reviewSubmission(submissionId).unwrap()

      setManualReview(mapCodeReviewResponseToFeedback(assignmentId, reviewResult))
    } catch (error) {
      toast({
        tone: "error",
        description: error instanceof Error ? error.message : "Không thể lấy AI review cho bài nộp này.",
      })
    } finally {
      setRunningAction(null)
    }
  }, [
    assignmentId,
    assignmentProblem?.id,
    code,
    handleTabChange,
    latestHistoricalReview,
    reviewSubmission,
    submissionId,
    submissionDetail?.isReviewed,
    toast,
  ])

  const loadRecommendation = useCallback(async () => {
    if (!assignmentProblem?.id || !currentUserId) {
      setRecommendationRoadmap(null)
      return
    }

    setIsRecommendationLoading(true)

    try {
      const roadmap = await getRecommendationRoadmap({
        student_id: currentUserId,
        current_exercise_id: assignmentProblem.id,
      }).unwrap()
      setRecommendationRoadmap(roadmap)
    } catch (error) {
      setRecommendationRoadmap(null)
      toast({
        tone: "error",
        description:
          error instanceof Error ? error.message : "Không thể tải gợi ý bài tập tiếp theo.",
      })
    } finally {
      setIsRecommendationLoading(false)
    }
  }, [assignmentProblem?.id, currentUserId, getRecommendationRoadmap, toast])

  const handleRecommendationDialogOpenChange = useCallback(
    (open: boolean) => {
      setIsRecommendationDialogOpen(open)

      if (open && !activeRecommendationRoadmap && !isRecommendationLoading) {
        void loadRecommendation()
      }
    },
    [activeRecommendationRoadmap, isRecommendationLoading, loadRecommendation]
  )

  if (
    isLoadingAssignment ||
    isLoadingSubmissions ||
    isLoadingProblem ||
    isLoadingTestcases ||
    isLoadingDetail ||
    isLoadingReviewHistory ||
    isLoadingRecommendationHistory
  ) {
    return <AttemptWorkspaceSkeleton title="Đang tải bài làm đã nộp..." />
  }

  if (
    assignmentError ||
    detailError ||
    !assignmentContext ||
    !assignment ||
    !problem ||
    !submission ||
    !submissionDetail ||
    !execution
  ) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Không tìm thấy bài làm để xem lại</CardTitle>
        </CardHeader>
        <CardContent>
          Quay lại assignment và chọn một submission hợp lệ từ lịch sử làm bài.
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <AssignmentAttemptHeader
        assignment={assignment}
        problem={problem}
        backHref={backHref}
        startedAtMs={Number.isNaN(startedAtMs) ? 0 : startedAtMs}
        timeLimitMinutes={assignmentContext.timeLimit ?? 0}
        language={language}
        languages={[language]}
        readOnly
        onLanguageChange={() => {}}
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
        <ProblemWorkspaceTabs
          problem={problem}
          activeTab={activeTab}
          onTabChange={handleTabChange}
          hasMounted={hasMounted}
          displayedExecution={execution}
          review={review}
          recommendationRoadmap={activeRecommendationRoadmap}
          role={role}
          isRecommendationLoading={isRecommendationLoading}
          isRecommendationDialogOpen={isRecommendationDialogOpen}
          runningAction={runningAction}
          canRequestReview
          allowRecommendation
          onLoadReview={loadReview}
          onRecommendationDialogOpenChange={handleRecommendationDialogOpenChange}
          reviewEmptyMessage="Nhấn Review Code để xem AI review và gợi ý bài tập tiếp theo."
          showExamplesSection={false}
        />

        <EditorWorkspaceCard
          language={language}
          code={code}
          runningAction={null}
          canRequestReview={false}
          readOnly
          hideActions
          helperTitle="Bài làm đã nộp"
          helperLines={[
            "Đây là mã nguồn đã được nộp cho submission này.",
            "Nhấn Review Code trong phần kết quả hoặc tab Code Review để xem nhận xét AI và gợi ý bài tập tiếp theo.",
          ]}
          onCodeChange={() => {}}
          onRun={() => {}}
          onSubmit={() => {}}
          onReview={() => {}}
        />
      </div>
    </div>
  )
}
