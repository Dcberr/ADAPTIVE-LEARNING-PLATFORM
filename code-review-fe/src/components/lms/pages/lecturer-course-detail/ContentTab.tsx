"use client"

import { memo } from "react"
import { Plus } from "lucide-react"

import TopicSectionCard from "@/components/lms/pages/lecturer-course-detail/TopicSectionCard"
import type {
  AssignmentDraft,
  TopicCard,
} from "@/components/lms/pages/lecturer-course-detail/types"

function ContentTabComponent({
  topicCards,
  editMode,
  collapsedTopics,
  onToggleTopic,
  onUpdateTopic,
  onDeleteTopic,
  onDeleteMaterial,
  onOpenResourceModal,
  onOpenAssignmentModal,
  onDeleteDraftAssignment,
  onAddSection,
}: {
  topicCards: TopicCard[]
  editMode: boolean
  collapsedTopics: Record<string, boolean>
  onToggleTopic: (topicId: string) => void
  onUpdateTopic: (topicId: string, patch: { title?: string; summary?: string }) => void
  onDeleteTopic: (topicId: string) => void
  onDeleteMaterial: (materialId: string) => void
  onOpenResourceModal: (topicId: string, materialId?: string) => void
  onOpenAssignmentModal: (topicId: string, draft?: AssignmentDraft) => void
  onDeleteDraftAssignment: (draftId: string) => void
  onAddSection: () => void
}) {
  return (
    <div className="mt-6 space-y-5">
      {topicCards.map((topic) => (
        <TopicSectionCard
          key={topic.id}
          topic={topic}
          collapsed={Boolean(collapsedTopics[topic.id])}
          editMode={editMode}
          onToggleTopic={onToggleTopic}
          onUpdateTopic={onUpdateTopic}
          onDeleteTopic={onDeleteTopic}
          onDeleteMaterial={onDeleteMaterial}
          onOpenResourceModal={onOpenResourceModal}
          onOpenAssignmentModal={onOpenAssignmentModal}
          onDeleteDraftAssignment={onDeleteDraftAssignment}
        />
      ))}

      {editMode ? (
        <button
          type="button"
          className="flex w-full items-center justify-center rounded-[2rem] border border-dashed border-slate-300 bg-white px-6 py-6 text-lg font-semibold text-[#0f84c2]"
          onClick={onAddSection}
        >
          <Plus className="mr-2 size-5" />
          Add section
        </button>
      ) : null}
    </div>
  )
}

const ContentTab = memo(ContentTabComponent)

export default ContentTab
