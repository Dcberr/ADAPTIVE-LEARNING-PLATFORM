import SubmissionReviewPage from "@/components/lms/pages/SubmissionReviewPage"

export default async function Page({
  params,
}: {
  params: Promise<{ id: string; submissionId: string }>
}) {
  const { id, submissionId } = await params

  return <SubmissionReviewPage assignmentId={id} submissionId={submissionId} role="lecturer" />
}
