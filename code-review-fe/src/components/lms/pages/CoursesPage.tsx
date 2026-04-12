"use client"

import { useMemo } from "react"

import CourseBrowser, {
  type CourseBrowserItem,
} from "@/components/lms/pages/course-browser/CourseBrowser"
import { useGetMyClassesQuery } from "@/store/redux/api/lmsApi"

export default function CoursesPage() {
  const {
    data: classes = [],
    error,
    isLoading,
  } = useGetMyClassesQuery()

  const items = useMemo<CourseBrowserItem[]>(
    () =>
      classes.map((course) => ({
        id: course.id,
        href: `/student/courses/${course.id}`,
        title: course.name,
        instructor: course.instructorName,
        schedule: course.schedule ?? "Lịch học đang cập nhật",
        enrolledCount: course.enrolledStudentsCount,
        imageUrl: course.imageUrl,
        seed: course.id,
        actionLabel: "Vào khóa học",
      })),
    [classes]
  )

  return (
    <CourseBrowser
      items={items}
      title="My Courses"
      description="Tìm nhanh khóa học và chuyển giữa dạng lưới hoặc danh sách như cùng một trải nghiệm thống nhất."
      emptyTitle={
        isLoading
          ? "Đang tải danh sách khóa học..."
          : error
            ? "Không tải được danh sách khóa học."
            : "Không tìm thấy khóa học phù hợp."
      }
      emptyDescription={
        isLoading
          ? "Dữ liệu khóa học đang được đồng bộ từ hệ thống."
          : error
            ? "Kiểm tra backend rồi thử lại sau."
            : "Thử đổi từ khóa tìm kiếm theo tên môn hoặc giảng viên."
      }
      searchPlaceholder="Tìm theo tên lớp, giảng viên hoặc lịch học..."
    />
  )
}
