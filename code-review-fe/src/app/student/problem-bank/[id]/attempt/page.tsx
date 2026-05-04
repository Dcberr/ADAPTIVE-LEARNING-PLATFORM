import CodeProblemPage from "@/components/lms/pages/CodeProblemPage"

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return <CodeProblemPage id={id} role="student" source="practice" />
}
