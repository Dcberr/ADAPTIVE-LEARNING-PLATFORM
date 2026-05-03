import ProblemBankSubmissionReviewPage from "@/components/lms/pages/ProblemBankSubmissionReviewPage"

export default async function Page({
  params,
}: {
  params: Promise<{ id: string; submissionId: string }>
}) {
  const { id, submissionId } = await params
  return (
    <ProblemBankSubmissionReviewPage
      problemId={id}
      submissionId={submissionId}
      role="lecturer"
    />
  )
}
