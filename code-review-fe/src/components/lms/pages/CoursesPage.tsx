"use client"

import { useMemo } from "react"

import CourseBrowser, {
  type CourseBrowserItem,
} from "@/components/lms/pages/course-browser/CourseBrowser"
import { courses } from "@/data/lms/mockData"
import { getMockCourseImageUrl } from "@/lib/mock-course-images"

export default function CoursesPage() {
  const items = useMemo<CourseBrowserItem[]>(
    () =>
      courses.map((course) => ({
        id: course.id,
        href: `/student/courses/${course.id}`,
        title: course.name,
        instructor: course.instructor,
        code: course.code,
        schedule: course.schedule,
        enrolledCount: course.enrolled,
        imageUrl: getMockCourseImageUrl(course.image),
        seed: `student-course-${course.id}`,
        actionLabel: "Vào khóa học",
      })),
    []
  )

  return (
    <CourseBrowser
      items={items}
      title="My Courses"
      description="Tìm nhanh khóa học và chuyển giữa dạng lưới hoặc danh sách như cùng một trải nghiệm thống nhất."
      emptyTitle="Không tìm thấy khóa học phù hợp."
      emptyDescription="Thử đổi từ khóa tìm kiếm theo tên môn, mã môn hoặc giảng viên."
      searchPlaceholder="Search courses by name, code, instructor, or schedule..."
    />
  )
}
