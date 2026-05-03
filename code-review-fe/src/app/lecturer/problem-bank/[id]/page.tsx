import ProblemBankProblemDetailPage from "@/components/lms/pages/ProblemBankProblemDetailPage"

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return <ProblemBankProblemDetailPage id={id} role="lecturer" />
}
