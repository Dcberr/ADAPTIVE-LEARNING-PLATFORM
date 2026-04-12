"use client"

import AssignmentDraftModalForm from "@/components/lms/pages/lecturer-course-detail/AssignmentDraftModalForm"
import ResourceModalForm, {
  type ResourceDraft,
} from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"
import TopicModalForm, {
  type TopicDraft,
} from "@/components/lms/pages/lecturer-course-detail/TopicModalForm"
import type { AssignmentDraft } from "@/components/lms/pages/lecturer-course-detail/types"
import SimpleModal from "@/components/lms/SimpleModal"

export default function ClassWorkspaceModals({
  topicModalOpen,
  resourceModalOpen,
  assignmentModalOpen,
  topicDraft,
  editingMaterialId,
  editingDraftId,
  resourceDraft,
  assignmentDraft,
  isSubmittingTopic,
  isSubmittingResource,
  isSubmittingAssignment,
  onCloseTopicModal,
  onCloseResourceModal,
  onCloseAssignmentModal,
  onTopicDraftChange,
  onResourceDraftChange,
  onAssignmentDraftChange,
  onSaveTopic,
  onSaveResource,
  onSaveAssignment,
}: {
  topicModalOpen: boolean
  resourceModalOpen: boolean
  assignmentModalOpen: boolean
  topicDraft: TopicDraft
  editingMaterialId: string | null
  editingDraftId: string | null
  resourceDraft: ResourceDraft
  assignmentDraft: AssignmentDraft
  isSubmittingTopic: boolean
  isSubmittingResource: boolean
  isSubmittingAssignment: boolean
  onCloseTopicModal: () => void
  onCloseResourceModal: () => void
  onCloseAssignmentModal: () => void
  onTopicDraftChange: (patch: Partial<TopicDraft>) => void
  onResourceDraftChange: (patch: Partial<ResourceDraft>) => void
  onAssignmentDraftChange: (patch: Partial<AssignmentDraft>) => void
  onSaveTopic: () => void
  onSaveResource: () => void
  onSaveAssignment: () => void
}) {
  return (
    <>
      <SimpleModal
        open={topicModalOpen}
        title="Thêm section"
        description="Nhập tên và mô tả cho topic mới trong lớp học."
        onClose={onCloseTopicModal}
      >
        <TopicModalForm
          draft={topicDraft}
          isSubmitting={isSubmittingTopic}
          onChange={onTopicDraftChange}
          onCancel={onCloseTopicModal}
          onSave={onSaveTopic}
        />
      </SimpleModal>

      <SimpleModal
        open={resourceModalOpen}
        title={editingMaterialId ? "Chỉnh sửa tài nguyên" : "Thêm tài nguyên"}
        description="Nhập thông tin file, video hoặc image resource cho section hiện tại."
        onClose={onCloseResourceModal}
      >
        <ResourceModalForm
          draft={resourceDraft}
          isSubmitting={isSubmittingResource}
          onChange={onResourceDraftChange}
          onCancel={onCloseResourceModal}
          onSave={onSaveResource}
        />
      </SimpleModal>

      <SimpleModal
        open={assignmentModalOpen}
        title={editingDraftId ? "Chỉnh sửa assignment" : "Thêm assignment"}
        description="Popup này mô phỏng form tạo assignment như bên LMS."
        onClose={onCloseAssignmentModal}
      >
        <AssignmentDraftModalForm
          draft={assignmentDraft}
          isSubmitting={isSubmittingAssignment}
          onChange={onAssignmentDraftChange}
          onCancel={onCloseAssignmentModal}
          onSave={onSaveAssignment}
        />
      </SimpleModal>
    </>
  )
}
