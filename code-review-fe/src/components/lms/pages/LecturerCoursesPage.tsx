"use client"

import { type FormEvent, useMemo, useState } from "react"
import { Plus } from "lucide-react"

import CourseBrowser, {
  type CourseBrowserItem,
} from "@/components/lms/pages/course-browser/CourseBrowser"
import SimpleModal from "@/components/lms/SimpleModal"
import { useToast } from "@/components/ui/toast-provider"
import {
  useCreateClassMutation,
  useGetMyClassesQuery,
} from "@/store/redux/api/lmsApi"
import CreateClassCard from "@/components/lms/pages/lecturer-courses/CreateClassCard"
import { Button } from "@/components/ui/button"

export default function LecturerCoursesPage() {
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [draft, setDraft] = useState({
    name: "",
    description: "",
    image: null as File | null,
    schedule: "",
  })
  const [highlightedClassId, setHighlightedClassId] = useState<string | null>(null)
  const { toast } = useToast()
  const {
    data: classes = [],
    error,
    isLoading,
  } = useGetMyClassesQuery()
  const [createClass, { isLoading: isCreating }] = useCreateClassMutation()

  const browserItems = useMemo<CourseBrowserItem[]>(
    () =>
      classes.map((item) => ({
        id: item.id,
        href: `/lecturer/courses/${item.id}`,
        title: item.name,
        instructor: item.instructorName,
        schedule: item.schedule ?? "Lịch học đang cập nhật",
        enrolledCount: item.enrolledStudentsCount,
        imageUrl: item.imageUrl,
        seed: item.id,
        actionLabel: "Mở lớp học",
        highlighted: item.id === highlightedClassId,
      })),
    [classes, highlightedClassId]
  )

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const name = draft.name.trim()
    const description = draft.description.trim()
    const image = draft.image
    const schedule = draft.schedule.trim()

    if (!name || !description) {
      toast({
        tone: "error",
        description: "Tên lớp và mô tả là bắt buộc.",
      })
      return
    }

    try {
      const createdClass = await createClass({ name, description, image, schedule }).unwrap()
      setDraft({ name: "", description: "", image: null, schedule: "" })
      setHighlightedClassId(createdClass.id)
      setCreateModalOpen(false)
      toast({
        tone: "success",
        description: `Đã tạo lớp "${createdClass.name}".`,
      })
    } catch {
      toast({
        tone: "error",
        description: "Không thể tạo lớp. Kiểm tra lại backend hoặc quyền hiện tại.",
      })
    }
  }

  return (
    <div className="space-y-6">
      {Boolean(error) ? (
        <CourseBrowser
          items={[]}
          title="Lớp học của bạn"
          isLoading={false}
          emptyTitle="Không tải được danh sách lớp."
          emptyDescription="Kiểm tra backend rồi thử refresh lại danh sách lớp."
          searchPlaceholder="Tìm theo tên lớp, giảng viên hoặc lịch học..."
          headerActions={
            <Button
              className="rounded-xl bg-[#1717ad] text-white hover:bg-[#1717ad]/90"
              onClick={() => setCreateModalOpen(true)}
            >
              <Plus className="size-4" />
              Tạo lớp
            </Button>
          }
        />
      ) : (
        <CourseBrowser
          items={browserItems}
          title="Lớp học của bạn"
          isLoading={isLoading}
          emptyTitle={isLoading ? "Đang tải lớp học..." : "Chưa có lớp học nào."}
          emptyDescription={
            isLoading
              ? "Danh sách lớp đang được đồng bộ từ backend."
              : "Dùng nút Tạo lớp để tạo lớp đầu tiên và bắt đầu quản lý nội dung, sinh viên."
          }
          searchPlaceholder="Tìm theo tên lớp, giảng viên hoặc lịch học..."
          headerActions={
            <Button
              className="rounded-xl bg-[#1717ad] text-white hover:bg-[#1717ad]/90"
              onClick={() => setCreateModalOpen(true)}
            >
              <Plus className="size-4" />
              Tạo lớp
            </Button>
          }
        />
      )}

      <SimpleModal
        open={createModalOpen}
        title="Tạo lớp mới"
        description="Nhập thông tin cơ bản cho lớp học mới của bạn."
        onClose={() => setCreateModalOpen(false)}
      >
        <CreateClassCard
          draft={draft}
          isCreating={isCreating}
          onChange={(patch) => setDraft((state) => ({ ...state, ...patch }))}
          onSubmit={handleSubmit}
        />
      </SimpleModal>
    </div>
  )
}
