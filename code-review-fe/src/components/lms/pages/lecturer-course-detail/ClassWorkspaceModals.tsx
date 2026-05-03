"use client"

import AssignmentDraftModalForm from "@/components/lms/pages/lecturer-course-detail/AssignmentDraftModalForm"
import AssignmentSettingsModalForm from "@/components/lms/pages/lecturer-course-detail/AssignmentSettingsModalForm"
import ConfirmActionModal from "@/components/lms/pages/lecturer-course-detail/ConfirmActionModal"
import ResourceModalForm, {
  type ResourceDraft,
} from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"
import TopicModalForm, {
  type TopicDraft,
} from "@/components/lms/pages/lecturer-course-detail/TopicModalForm"
import type {
  AssignmentDraft,
  AssignmentSettingsDraft,
} from "@/components/lms/pages/lecturer-course-detail/types"
import CreateClassCard from "@/components/lms/pages/lecturer-courses/CreateClassCard"
import SimpleModal from "@/components/lms/SimpleModal"

export type ClassDraft = {
  name: string
  description: string
  image: File | null
  schedule: string
}

export type DeleteTarget =
  | {
      type: "class"
      id: string
      title: string
      description: string
    }
  | {
      type: "topic"
      id: string
      title: string
      description: string
    }
  | {
      type: "document"
      id: string
      title: string
      description: string
    }
  | {
      type: "assignment"
      id: string
      title: string
      description: string
    }

export default function ClassWorkspaceModals({
  classModalOpen,
  topicModalOpen,
  resourceModalOpen,
  assignmentCreateModalOpen,
  assignmentEditModalOpen,
  deleteTarget,
  classDraft,
  topicDraft,
  editingTopicId,
  editingMaterialId,
  resourceDraft,
  assignmentDraft,
  assignmentSettingsDraft,
  isSubmittingClass,
  isSubmittingTopic,
  isSubmittingResource,
  isSubmittingAssignment,
  isSubmittingAssignmentSettings,
  isDeleting,
  onCloseClassModal,
  onCloseTopicModal,
  onCloseResourceModal,
  onCloseAssignmentCreateModal,
  onCloseAssignmentEditModal,
  onCloseDeleteModal,
  onClassDraftChange,
  onTopicDraftChange,
  onResourceDraftChange,
  onAssignmentDraftChange,
  onAssignmentSettingsDraftChange,
  onSaveClass,
  onSaveTopic,
  onSaveResource,
  onSaveAssignment,
  onSaveAssignmentSettings,
  onConfirmDelete,
}: {
  classModalOpen: boolean
  topicModalOpen: boolean
  resourceModalOpen: boolean
  assignmentCreateModalOpen: boolean
  assignmentEditModalOpen: boolean
  deleteTarget: DeleteTarget | null
  classDraft: ClassDraft
  topicDraft: TopicDraft
  editingTopicId: string | null
  editingMaterialId: string | null
  resourceDraft: ResourceDraft
  assignmentDraft: AssignmentDraft
  assignmentSettingsDraft: AssignmentSettingsDraft
  isSubmittingClass: boolean
  isSubmittingTopic: boolean
  isSubmittingResource: boolean
  isSubmittingAssignment: boolean
  isSubmittingAssignmentSettings: boolean
  isDeleting: boolean
  onCloseClassModal: () => void
  onCloseTopicModal: () => void
  onCloseResourceModal: () => void
  onCloseAssignmentCreateModal: () => void
  onCloseAssignmentEditModal: () => void
  onCloseDeleteModal: () => void
  onClassDraftChange: (patch: Partial<ClassDraft>) => void
  onTopicDraftChange: (patch: Partial<TopicDraft>) => void
  onResourceDraftChange: (patch: Partial<ResourceDraft>) => void
  onAssignmentDraftChange: (patch: Partial<AssignmentDraft>) => void
  onAssignmentSettingsDraftChange: (patch: Partial<AssignmentSettingsDraft>) => void
  onSaveClass: () => void
  onSaveTopic: () => void
  onSaveResource: () => void
  onSaveAssignment: () => void
  onSaveAssignmentSettings: () => void
  onConfirmDelete: () => void
}) {
  return (
    <>
      <SimpleModal
        open={classModalOpen}
        title="Chỉnh sửa lớp học"
        description="Cập nhật thông tin cơ bản của lớp. Có thể bỏ qua ảnh nếu không muốn thay đổi."
        onClose={onCloseClassModal}
      >
        <CreateClassCard
          draft={classDraft}
          isCreating={isSubmittingClass}
          submitLabel="Lưu thông tin lớp"
          submittingLabel="Đang lưu lớp..."
          descriptionHint="Backend không trả về mô tả hiện tại. Nếu để trống và không chỉnh trường này, hệ thống sẽ giữ nguyên mô tả cũ."
          onChange={onClassDraftChange}
          onSubmit={(event) => {
            event.preventDefault()
            onSaveClass()
          }}
        />
      </SimpleModal>

      <SimpleModal
        open={topicModalOpen}
        title={editingTopicId ? "Chỉnh sửa section" : "Thêm section"}
        description={
          editingTopicId
            ? "Cập nhật tên và mô tả cho section hiện tại."
            : "Nhập tên và mô tả cho topic mới trong lớp học."
        }
        onClose={onCloseTopicModal}
      >
        <TopicModalForm
          draft={topicDraft}
          isSubmitting={isSubmittingTopic}
          submitLabel={editingTopicId ? "Lưu section" : "Tạo section"}
          submittingLabel={editingTopicId ? "Đang cập nhật..." : "Đang tạo..."}
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
          submitLabel={editingMaterialId ? "Lưu tài nguyên" : "Thêm tài nguyên"}
          submittingLabel={editingMaterialId ? "Đang cập nhật..." : "Đang upload..."}
          fileHint={
            editingMaterialId
              ? "Có thể bỏ qua nếu muốn giữ nguyên file hiện tại."
              : "Chọn file tài nguyên để upload."
          }
          onChange={onResourceDraftChange}
          onCancel={onCloseResourceModal}
          onSave={onSaveResource}
        />
      </SimpleModal>

      <SimpleModal
        open={assignmentCreateModalOpen}
        title="Thêm assignment"
        description="Tạo bài tập mới với đề bài, starter code và test case."
        onClose={onCloseAssignmentCreateModal}
      >
        <AssignmentDraftModalForm
          draft={assignmentDraft}
          isSubmitting={isSubmittingAssignment}
          onChange={onAssignmentDraftChange}
          onCancel={onCloseAssignmentCreateModal}
          onSave={onSaveAssignment}
        />
      </SimpleModal>

      <SimpleModal
        open={assignmentEditModalOpen}
        title="Chỉnh sửa assignment"
        description="Cập nhật metadata của assignment theo đúng phần backend hiện hỗ trợ."
        onClose={onCloseAssignmentEditModal}
      >
        <AssignmentSettingsModalForm
          draft={assignmentSettingsDraft}
          isSubmitting={isSubmittingAssignmentSettings}
          onChange={onAssignmentSettingsDraftChange}
          onCancel={onCloseAssignmentEditModal}
          onSave={onSaveAssignmentSettings}
        />
      </SimpleModal>

      <ConfirmActionModal
        open={Boolean(deleteTarget)}
        title={deleteTarget ? `Xóa ${deleteTarget.title}` : "Xác nhận xóa"}
        description={deleteTarget?.description ?? ""}
        confirmLabel={
          deleteTarget?.type === "class"
            ? "Xóa lớp"
            : deleteTarget?.type === "topic"
              ? "Xóa section"
              : deleteTarget?.type === "document"
                ? "Xóa tài nguyên"
                : "Xóa assignment"
        }
        isSubmitting={isDeleting}
        onClose={onCloseDeleteModal}
        onConfirm={onConfirmDelete}
      />
    </>
  )
}
