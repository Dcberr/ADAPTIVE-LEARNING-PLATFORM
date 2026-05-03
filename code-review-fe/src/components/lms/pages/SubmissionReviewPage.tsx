"use client"

import { useMemo } from "react"

import { AttemptWorkspaceSkeleton } from "@/components/lms/LmsLoadingStates"
import type { UserRole } from "@/data/lms/extendedMockData"
import AssignmentAttemptHeader from "@/components/lms/pages/code-problem/AssignmentAttemptHeader"
import EditorWorkspaceCard from "@/components/lms/pages/code-problem/EditorWorkspaceCard"
import ProblemWorkspaceTabs from "@/components/lms/pages/code-problem/ProblemWorkspaceTabs"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Assignment, CodingProblem } from "@/data/lms/mockData"
import type { ExecutionSummary } from "@/services/lms/mockLmsService"
import {
  type AssignmentContext,
  type AssignmentProblemResponse,
  type AssignmentSubmissionResponse,
  type AssignmentTestcaseResponse,
  type SubmissionDetailResponse,
  useGetAssignmentContextQuery,
  useGetAssignmentProblemQuery,
  useGetAssignmentSubmissionsQuery,
  useGetAssignmentTestcasesQuery,
  useGetSubmissionByIdQuery,
} from "@/store/redux/api/lmsApi"

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
    examples: visibleExamples,
    constraints: assignmentProblem?.problemConstraint
      ? assignmentProblem.problemConstraint
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean)
      : [],
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
    eligibleForReview: false,
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
  const code = submissionDetail?.code ?? ""
  const language = submissionDetail?.language ?? "cpp"
  const backHref = `/${role}/assignments/${assignmentId}`
  const startedAtMs = submission?.startedAt ? new Date(submission.startedAt).getTime() : 0

  if (
    isLoadingAssignment ||
    isLoadingSubmissions ||
    isLoadingProblem ||
    isLoadingTestcases ||
    isLoadingDetail
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

      <div className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
        <ProblemWorkspaceTabs
          problem={problem}
          activeTab={activeTab}
          onTabChange={handleTabChange}
          hasMounted={hasMounted}
          displayedExecution={execution}
          review={null}
          recommendedProblems={[]}
          runningAction={null}
          canRequestReview={false}
          onLoadReview={() => {}}
        />

        <EditorWorkspaceCard
          language={language}
          code={code}
          runningAction={null}
          canRequestReview={false}
          readOnly
          hideActions
          helperTitle="Review snapshot"
          helperLines={[
            `Submission ID: ${submission.submissionId}`,
            `Started at: ${submission.startedAt}`,
            `Submitted at: ${submission.submittedAt}`,
            "Đây là bản xem lại của lần nộp đã chốt, không thể chỉnh sửa hoặc gửi lại từ màn này.",
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
