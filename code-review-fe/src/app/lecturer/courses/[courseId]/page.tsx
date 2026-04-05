import LecturerCourseDetailPage from "@/components/lms/pages/LecturerCourseDetailPage"

export default async function Page({ params }: { params: Promise<{ courseId: string }> }) {
  const { courseId } = await params
  return <LecturerCourseDetailPage classId={courseId} />
}
