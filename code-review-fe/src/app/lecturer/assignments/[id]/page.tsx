import AssignmentDetailPage from "@/components/lms/pages/AssignmentDetailPage"

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return <AssignmentDetailPage id={id} role="lecturer" />
}
