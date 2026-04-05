"use client"

import { type FormEvent, useState } from "react"

import {
  useCreateClassMutation,
  useGetMyClassesQuery,
} from "@/store/redux/api/lmsApi"
import ClassesGrid from "@/components/lms/pages/lecturer-courses/ClassesGrid"
import ClassesOverviewCard from "@/components/lms/pages/lecturer-courses/ClassesOverviewCard"
import CreateClassCard from "@/components/lms/pages/lecturer-courses/CreateClassCard"

type FeedbackState =
  | {
      tone: "success" | "error"
      message: string
    }
  | null

export default function LecturerCoursesPage() {
  const [draft, setDraft] = useState({ name: "", description: "" })
  const [feedback, setFeedback] = useState<FeedbackState>(null)
  const [highlightedClassId, setHighlightedClassId] = useState<string | null>(null)
  const {
    data: classes = [],
    error,
    isLoading,
    refetch,
  } = useGetMyClassesQuery()
  const [createClass, { isLoading: isCreating }] = useCreateClassMutation()

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const name = draft.name.trim()
    const description = draft.description.trim()

    if (!name || !description) {
      setFeedback({
        tone: "error",
        message: "Tên lớp và mô tả là bắt buộc.",
      })
      return
    }

    try {
      const createdClass = await createClass({ name, description }).unwrap()
      setDraft({ name: "", description: "" })
      setHighlightedClassId(createdClass.id)
      setFeedback({
        tone: "success",
        message: `Đã tạo lớp "${createdClass.name}".`,
      })
    } catch {
      setFeedback({
        tone: "error",
        message: "Không thể tạo lớp. Kiểm tra lại backend hoặc quyền hiện tại.",
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <ClassesOverviewCard
          classCount={classes.length}
          enrolledStudentCount={classes.reduce((sum, item) => sum + item.enrolledStudentsCount, 0)}
        />
        <CreateClassCard
          draft={draft}
          feedback={feedback}
          isCreating={isCreating}
          onChange={(patch) => setDraft((state) => ({ ...state, ...patch }))}
          onSubmit={handleSubmit}
        />
      </div>

      <ClassesGrid
        classes={classes}
        isLoading={isLoading}
        hasError={Boolean(error)}
        highlightedClassId={highlightedClassId}
        onRetry={refetch}
      />
    </div>
  )
}
