"use client"

import { memo } from "react"
import { Plus } from "lucide-react"

import TopicSectionCard from "@/components/lms/pages/lecturer-course-detail/TopicSectionCard"
import type { TopicCard } from "@/components/lms/pages/lecturer-course-detail/types"

function ContentTabComponent({
  topicCards,
  editMode,
  collapsedTopics,
  onToggleTopic,
  onEditTopic,
  onDeleteTopic,
  onDeleteMaterial,
  onOpenResourceModal,
  onOpenAssignmentModal,
  onEditAssignment,
  onDeleteAssignment,
  onAddSection,
  assignmentHrefPrefix,
}: {
  topicCards: TopicCard[]
  editMode: boolean
  collapsedTopics: Record<string, boolean>
  onToggleTopic: (topicId: string) => void
  onEditTopic: (topicId: string) => void
  onDeleteTopic: (topicId: string) => void
  onDeleteMaterial: (materialId: string) => void
  onOpenResourceModal: (topicId: string, materialId?: string) => void
  onOpenAssignmentModal: (topicId: string) => void
  onEditAssignment: (assignmentId: string) => void
  onDeleteAssignment: (assignmentId: string) => void
  onAddSection: () => void
  assignmentHrefPrefix?: string
}) {
  return (
    <div className="mt-6 space-y-5">
      {topicCards.length === 0 ? (
        <div className="rounded-[2rem] border border-dashed border-slate-300 bg-white px-6 py-10 text-center">
          <p className="text-lg font-semibold text-[#030391]">Hiện chưa có topic nào</p>
          <p className="mt-2 text-sm text-slate-500">
            {editMode
              ? "Hãy thêm section đầu tiên để bắt đầu tổ chức nội dung cho lớp học này."
              : "Bật chế độ chỉnh sửa rồi thêm section đầu tiên cho lớp học này."}
          </p>
          {editMode ? (
            <button
              type="button"
              className="mt-5 inline-flex items-center justify-center rounded-full bg-[#1488D8] px-5 py-2 text-sm font-semibold text-white hover:bg-[#1488D8]/90"
              onClick={onAddSection}
            >
              <Plus className="mr-2 size-4" />
              Thêm section đầu tiên
            </button>
          ) : null}
        </div>
      ) : null}

      {topicCards.map((topic) => (
        <TopicSectionCard
          key={topic.id}
          topic={topic}
          collapsed={Boolean(collapsedTopics[topic.id])}
          editMode={editMode}
          onToggleTopic={onToggleTopic}
          onEditTopic={onEditTopic}
          onDeleteTopic={onDeleteTopic}
          onDeleteMaterial={onDeleteMaterial}
          onOpenResourceModal={onOpenResourceModal}
          onOpenAssignmentModal={onOpenAssignmentModal}
          onEditAssignment={onEditAssignment}
          onDeleteAssignment={onDeleteAssignment}
          assignmentHrefPrefix={assignmentHrefPrefix}
        />
      ))}

      {editMode ? (
        <button
          type="button"
          className="flex w-full items-center justify-center rounded-[2rem] border border-dashed border-slate-300 bg-white px-6 py-6 text-lg font-semibold text-[#0f84c2]"
          onClick={onAddSection}
        >
          <Plus className="mr-2 size-5" />
          Thêm section
        </button>
      ) : null}
    </div>
  )
}

const ContentTab = memo(ContentTabComponent)

export default ContentTab
