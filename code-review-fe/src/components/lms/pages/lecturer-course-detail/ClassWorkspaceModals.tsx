"use client"

import AssignmentDraftModalForm from "@/components/lms/pages/lecturer-course-detail/AssignmentDraftModalForm"
import ResourceModalForm, {
  type ResourceDraft,
} from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"
import type { AssignmentDraft } from "@/components/lms/pages/lecturer-course-detail/types"
import SimpleModal from "@/components/lms/SimpleModal"

export default function ClassWorkspaceModals({
  resourceModalOpen,
  assignmentModalOpen,
  editingMaterialId,
  editingDraftId,
  resourceDraft,
  assignmentDraft,
  onCloseResourceModal,
  onCloseAssignmentModal,
  onResourceDraftChange,
  onAssignmentDraftChange,
  onSaveResource,
  onSaveAssignment,
}: {
  resourceModalOpen: boolean
  assignmentModalOpen: boolean
  editingMaterialId: string | null
  editingDraftId: string | null
  resourceDraft: ResourceDraft
  assignmentDraft: AssignmentDraft
  onCloseResourceModal: () => void
  onCloseAssignmentModal: () => void
  onResourceDraftChange: (patch: Partial<ResourceDraft>) => void
  onAssignmentDraftChange: (patch: Partial<AssignmentDraft>) => void
  onSaveResource: () => void
  onSaveAssignment: () => void
}) {
  return (
    <>
      <SimpleModal
        open={resourceModalOpen}
        title={editingMaterialId ? "Chỉnh sửa tài nguyên" : "Thêm tài nguyên"}
        description="Nhập thông tin file, video hoặc image resource cho section hiện tại."
        onClose={onCloseResourceModal}
      >
        <ResourceModalForm
          draft={resourceDraft}
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
          onChange={onAssignmentDraftChange}
          onCancel={onCloseAssignmentModal}
          onSave={onSaveAssignment}
        />
      </SimpleModal>
    </>
  )
}
