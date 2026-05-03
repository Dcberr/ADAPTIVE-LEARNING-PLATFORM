"use client"

import { useCallback, useMemo, useState, type FormEvent } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

import { ClassWorkspaceSkeleton } from "@/components/lms/LmsLoadingStates"
import ClassWorkspaceHeader from "@/components/lms/pages/lecturer-course-detail/ClassWorkspaceHeader"
import ClassWorkspaceModals, {
  type ClassDraft,
  type DeleteTarget,
} from "@/components/lms/pages/lecturer-course-detail/ClassWorkspaceModals"
import ClassWorkspaceTabs from "@/components/lms/pages/lecturer-course-detail/ClassWorkspaceTabs"
import {
  emptyAssignmentDraft,
  emptyAssignmentSettingsDraft,
  emptyResourceDraft,
  formatClassDate,
} from "@/components/lms/pages/lecturer-course-detail/constants"
import { type ResourceDraft } from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"
import { type TopicDraft } from "@/components/lms/pages/lecturer-course-detail/TopicModalForm"
import type { AssignmentSettingsDraft } from "@/components/lms/pages/lecturer-course-detail/types"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { getBackendBaseUrl } from "@/lib/auth"
import { saveCachedAssignmentProblem } from "@/lib/assignment-problem-cache"
import {
  useAddStudentToClassMutation,
  useCreateAssignmentMutation,
  useCreateDocumentMutation,
  useCreateTopicMutation,
  useDeleteAssignmentMutation,
  useDeleteClassMutation,
  useDeleteDocumentMutation,
  useDeleteTopicMutation,
  useGetClassByIdQuery,
  useGetClassStudentsQuery,
  useGetClassTopicsQuery,
  useRemoveStudentFromClassMutation,
  useUpdateAssignmentMutation,
  useUpdateClassMutation,
  useUpdateDocumentMutation,
  useUpdateTopicMutation,
} from "@/store/redux/api/lmsApi"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/toast-provider"

type LecturerTab = "content" | "students"

function formatDateTimeLocal(value?: string | null) {
  if (!value) {
    return ""
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return ""
  }

  const timezoneOffset = date.getTimezoneOffset() * 60_000
  return new Date(date.getTime() - timezoneOffset).toISOString().slice(0, 16)
}

export default function LecturerCourseDetailPage({ classId }: { classId: string }) {
  const router = useRouter()
  const [editMode, setEditMode] = useState(false)
  const [collapsedTopics, setCollapsedTopics] = useState<Record<string, boolean>>({})
  const [classModalOpen, setClassModalOpen] = useState(false)
  const [topicModalOpen, setTopicModalOpen] = useState(false)
  const [resourceModalOpen, setResourceModalOpen] = useState(false)
  const [assignmentCreateModalOpen, setAssignmentCreateModalOpen] = useState(false)
  const [assignmentEditModalOpen, setAssignmentEditModalOpen] = useState(false)
  const [editingTopicId, setEditingTopicId] = useState<string | null>(null)
  const [editingMaterialId, setEditingMaterialId] = useState<string | null>(null)
  const [editingAssignmentId, setEditingAssignmentId] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  const [classDraft, setClassDraft] = useState<ClassDraft>({
    name: "",
    description: "",
    image: null,
    schedule: "",
  })
  const [isClassDescriptionDirty, setIsClassDescriptionDirty] = useState(false)
  const [topicDraft, setTopicDraft] = useState<TopicDraft>({ title: "", description: "" })
  const [resourceDraft, setResourceDraft] = useState<ResourceDraft>(emptyResourceDraft)
  const [assignmentDraft, setAssignmentDraft] = useState(emptyAssignmentDraft)
  const [assignmentSettingsDraft, setAssignmentSettingsDraft] = useState<AssignmentSettingsDraft>(
    emptyAssignmentSettingsDraft
  )
  const [userCode, setUserCode] = useState("")
  const [recentStudentIds, setRecentStudentIds] = useState<string[]>([])
  const [removingStudentCode, setRemovingStudentCode] = useState<string | null>(null)
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<LecturerTab>("content")
  const shouldLoadStudents = hasMounted("students")
  const { toast } = useToast()
  const {
    data: classroom,
    error,
    isFetching,
    isLoading,
    refetch,
  } = useGetClassByIdQuery(classId)
  const {
    data: enrolledStudents = [],
    isFetching: isFetchingStudents,
    isLoading: isLoadingStudents,
    refetch: refetchStudents,
  } = useGetClassStudentsQuery(classId, {
    skip: !shouldLoadStudents,
  })
  const {
    data: topicDetails = [],
    isFetching: isFetchingTopics,
    refetch: refetchTopics,
  } = useGetClassTopicsQuery(classId)
  const [addStudentToClass, { isLoading: isAddingStudent }] = useAddStudentToClassMutation()
  const [removeStudentFromClass, { isLoading: isRemovingStudent }] =
    useRemoveStudentFromClassMutation()
  const [createDocument, { isLoading: isCreatingDocument }] = useCreateDocumentMutation()
  const [updateDocument, { isLoading: isUpdatingDocument }] = useUpdateDocumentMutation()
  const [deleteDocument, { isLoading: isDeletingDocument }] = useDeleteDocumentMutation()
  const [createAssignment, { isLoading: isCreatingAssignment }] = useCreateAssignmentMutation()
  const [updateAssignment, { isLoading: isUpdatingAssignment }] = useUpdateAssignmentMutation()
  const [deleteAssignment, { isLoading: isDeletingAssignment }] = useDeleteAssignmentMutation()
  const [createTopic, { isLoading: isCreatingTopic }] = useCreateTopicMutation()
  const [updateTopic, { isLoading: isUpdatingTopic }] = useUpdateTopicMutation()
  const [deleteTopic, { isLoading: isDeletingTopic }] = useDeleteTopicMutation()
  const [updateClass, { isLoading: isUpdatingClass }] = useUpdateClassMutation()
  const [deleteClass, { isLoading: isDeletingClass }] = useDeleteClassMutation()
  const backendBaseUrl = getBackendBaseUrl()

  const bundle = useMemo(() => {
    if (!classroom) {
      return null
    }

    const normalizeMaterialType = (value: string): "file" | "video" | "image" => {
      if (value === "video" || value === "image") {
        return value
      }

      return "file"
    }

    const topics = topicDetails.map((topic, index) => ({
      id: topic.id,
      courseId: classId,
      order: index + 1,
      title: topic.title,
      summary: topic.description,
      materials: topic.documents.map((document) => ({
        id: document.id,
        title: document.title,
        description: document.description,
        resourceUrl: `${backendBaseUrl}/documents/download/${document.id}`,
        type: normalizeMaterialType(document.type),
        fileSize: "",
        previewLabel: document.type?.toUpperCase?.() ?? "FILE",
      })),
      assignments: topic.assignments.map((assignment) => ({
        id: assignment.id,
        title: assignment.title,
        deadline: assignment.deadline,
        startTime: assignment.startTime,
        timeLimit: assignment.timeLimit,
        maxScore: assignment.maxScore,
        maxSubmission: assignment.maxSubmission,
        tags: assignment.tags,
        difficulty: assignment.difficulty,
        status: assignment.status,
      })),
      customAssignments: [],
    }))

    return {
      course: {
        id: classId,
        code: classroom.status,
        name: classroom.name,
        description: `Instructor ${classroom.instructorName} • ${enrolledStudents.length} students • ${
          classroom.schedule ?? "Schedule chưa cấu hình"
        } • Created ${formatClassDate(classroom.createdAt)}`,
        color: "bg-[#030391]",
      },
      topics,
      assignments: topics.flatMap((topic) => topic.assignments),
    }
  }, [backendBaseUrl, classId, classroom, enrolledStudents.length, topicDetails])

  const resolvedEnrolledStudentsCount =
    shouldLoadStudents && !isLoadingStudents
      ? enrolledStudents.length
      : classroom?.enrolledStudentsCount ?? 0

  const topicCards = useMemo(() => bundle?.topics ?? [], [bundle])

  const resetClassModal = useCallback(() => {
    setClassModalOpen(false)
    setIsClassDescriptionDirty(false)
    setClassDraft({
      name: "",
      description: "",
      image: null,
      schedule: "",
    })
  }, [])

  const resetTopicModal = useCallback(() => {
    setTopicModalOpen(false)
    setEditingTopicId(null)
    setTopicDraft({ title: "", description: "" })
  }, [])

  const resetResourceModal = useCallback(() => {
    setResourceModalOpen(false)
    setEditingMaterialId(null)
    setResourceDraft(emptyResourceDraft)
  }, [])

  const resetAssignmentCreateModal = useCallback(() => {
    setAssignmentCreateModalOpen(false)
    setAssignmentDraft(emptyAssignmentDraft)
  }, [])

  const resetAssignmentEditModal = useCallback(() => {
    setAssignmentEditModalOpen(false)
    setEditingAssignmentId(null)
    setAssignmentSettingsDraft(emptyAssignmentSettingsDraft)
  }, [])

  const openClassModal = useCallback(() => {
    if (!classroom) {
      return
    }

    setClassDraft({
      name: classroom.name,
      description: "",
      image: null,
      schedule: classroom.schedule ?? "",
    })
    setClassModalOpen(true)
  }, [classroom])

  const openTopicModal = useCallback(
    (topicId?: string) => {
      const topic = topicCards.find((item) => item.id === topicId)

      setEditingTopicId(topic?.id ?? null)
      setTopicDraft(
        topic
          ? {
              title: topic.title,
              description: topic.summary,
            }
          : { title: "", description: "" }
      )
      setTopicModalOpen(true)
    },
    [topicCards]
  )

  const openResourceModal = useCallback(
    (topicId: string, materialId?: string) => {
      const topic = topicCards.find((item) => item.id === topicId)
      const material = topic?.materials.find((item) => item.id === materialId)

      setEditingMaterialId(material?.id ?? null)
      setResourceDraft(
        material
          ? {
              topicId,
              title: material.title,
              description: material.description,
              file: null,
            }
          : { ...emptyResourceDraft, topicId }
      )
      setResourceModalOpen(true)
    },
    [topicCards]
  )

  const openAssignmentCreateModal = useCallback((topicId: string) => {
    setAssignmentDraft({ ...emptyAssignmentDraft, topicId })
    setAssignmentCreateModalOpen(true)
  }, [])

  const openAssignmentEditModal = useCallback(
    (assignmentId: string) => {
      const topic = topicCards.find((item) =>
        item.assignments.some((assignment) => assignment.id === assignmentId)
      )
      const assignment = topic?.assignments.find((item) => item.id === assignmentId)

      if (!topic || !assignment) {
        toast({
          tone: "error",
          description: "Không tìm thấy assignment để chỉnh sửa.",
        })
        return
      }

      setEditingAssignmentId(assignment.id)
      setAssignmentSettingsDraft({
        id: assignment.id,
        topicId: topic.id,
        title: assignment.title,
        difficulty: assignment.difficulty as AssignmentSettingsDraft["difficulty"],
        score:
          typeof assignment.maxScore === "number" && Number.isFinite(assignment.maxScore)
            ? String(assignment.maxScore)
            : "",
        timeLimit:
          typeof assignment.timeLimit === "number" && Number.isFinite(assignment.timeLimit)
            ? String(assignment.timeLimit)
            : "",
        openAt: formatDateTimeLocal(assignment.startTime),
        deadline: formatDateTimeLocal(assignment.deadline),
        attemptsAllowed:
          typeof assignment.maxSubmission === "number" && Number.isFinite(assignment.maxSubmission)
            ? String(assignment.maxSubmission)
            : "",
        tags: (assignment.tags ?? []).join(", "),
      })
      setAssignmentEditModalOpen(true)
    },
    [toast, topicCards]
  )

  const requestDeleteClass = useCallback(() => {
    if (!bundle) {
      return
    }

    setDeleteTarget({
      type: "class",
      id: classId,
      title: bundle.course.name,
      description: `Lớp "${bundle.course.name}" sẽ bị xóa mềm khỏi hệ thống. Hãy chắc chắn bạn không còn cần truy cập workspace này nữa.`,
    })
  }, [bundle, classId])

  const requestDeleteTopic = useCallback(
    (topicId: string) => {
      const topic = topicCards.find((item) => item.id === topicId)
      if (!topic) {
        return
      }

      setDeleteTarget({
        type: "topic",
        id: topicId,
        title: topic.title,
        description: `Section "${topic.title}" cùng toàn bộ tài nguyên và bài tập liên quan sẽ không còn hiển thị trong lớp.`,
      })
    },
    [topicCards]
  )

  const requestDeleteDocument = useCallback(
    (documentId: string) => {
      const material = topicCards.flatMap((topic) => topic.materials).find((item) => item.id === documentId)
      if (!material) {
        return
      }

      setDeleteTarget({
        type: "document",
        id: documentId,
        title: material.title,
        description: `Tài nguyên "${material.title}" sẽ bị gỡ khỏi section hiện tại.`,
      })
    },
    [topicCards]
  )

  const requestDeleteAssignment = useCallback(
    (assignmentId: string) => {
      const assignment = topicCards
        .flatMap((topic) => topic.assignments)
        .find((item) => item.id === assignmentId)

      if (!assignment) {
        return
      }

      setDeleteTarget({
        type: "assignment",
        id: assignmentId,
        title: assignment.title,
        description: `Assignment "${assignment.title}" sẽ bị xóa mềm và không còn hiển thị trong section.`,
      })
    },
    [topicCards]
  )

  const handleAddSection = useCallback(() => {
    openTopicModal()
  }, [openTopicModal])

  const handleSaveClass = useCallback(() => {
    const name = classDraft.name.trim()

    if (!name) {
      toast({
        tone: "error",
        description: "Tên lớp học là bắt buộc.",
      })
      return
    }

    void updateClass({
      classId,
      name,
      description: isClassDescriptionDirty ? classDraft.description.trim() : undefined,
      schedule: classDraft.schedule.trim(),
      image: classDraft.image,
    })
      .unwrap()
      .then(() => {
        resetClassModal()
        toast({
          tone: "success",
          description: "Đã cập nhật thông tin lớp học.",
        })
      })
      .catch(() => {
        toast({
          tone: "error",
          description: "Không thể cập nhật lớp học. Kiểm tra lại backend rồi thử lại.",
        })
      })
  }, [classDraft, classId, isClassDescriptionDirty, resetClassModal, toast, updateClass])

  const handleSaveTopic = useCallback(() => {
    const title = topicDraft.title.trim()
    const description = topicDraft.description.trim()

    if (!title || !description) {
      toast({
        tone: "error",
        description: "Tên section và mô tả là bắt buộc.",
      })
      return
    }

    const action = editingTopicId
      ? updateTopic({
          classId,
          topicId: editingTopicId,
          title,
          description,
        }).unwrap()
      : createTopic({
          classId,
          title,
          description,
        }).unwrap()

    void action
      .then(() => {
        resetTopicModal()
        toast({
          tone: "success",
          description: editingTopicId
            ? "Đã cập nhật section."
            : "Đã thêm section mới cho lớp học.",
        })
      })
      .catch(() => {
        toast({
          tone: "error",
          description: editingTopicId
            ? "Không thể cập nhật section. Kiểm tra lại backend rồi thử lại."
            : "Không thể tạo topic mới. Kiểm tra lại backend rồi thử lại.",
        })
      })
  }, [classId, createTopic, editingTopicId, resetTopicModal, toast, topicDraft, updateTopic])

  const handleSaveMaterial = useCallback(() => {
    const title = resourceDraft.title.trim()
    const description = resourceDraft.description.trim()
    const file = resourceDraft.file

    if (!resourceDraft.topicId || !title || !description) {
      toast({
        tone: "error",
        description: "Tên tài nguyên và mô tả là bắt buộc.",
      })
      return
    }

    if (!editingMaterialId && !file) {
      toast({
        tone: "error",
        description: "Bạn cần chọn file khi tạo tài nguyên mới.",
      })
      return
    }

    const action = editingMaterialId
      ? updateDocument({
          classId,
          topicId: resourceDraft.topicId,
          documentId: editingMaterialId,
          title,
          description,
          file,
        }).unwrap()
      : createDocument({
          classId,
          topicId: resourceDraft.topicId,
          title,
          description,
          file: file as File,
        }).unwrap()

    void action
      .then(() => {
        resetResourceModal()
        toast({
          tone: "success",
          description: editingMaterialId
            ? "Đã cập nhật tài nguyên."
            : "Đã thêm tài nguyên cho section.",
        })
      })
      .catch(() => {
        toast({
          tone: "error",
          description: editingMaterialId
            ? "Không thể cập nhật tài nguyên. Kiểm tra lại backend rồi thử lại."
            : "Không thể upload tài nguyên. Kiểm tra lại backend rồi thử lại.",
        })
      })
  }, [
    classId,
    createDocument,
    editingMaterialId,
    resetResourceModal,
    resourceDraft,
    toast,
    updateDocument,
  ])

  const handleSaveAssignment = useCallback(() => {
    if (
      !assignmentDraft.title.trim() ||
      !assignmentDraft.description.trim() ||
      !assignmentDraft.openAt ||
      !assignmentDraft.deadline ||
      !assignmentDraft.timeLimit
    ) {
      toast({
        tone: "error",
        description: "Tiêu đề, mô tả, thời điểm mở, deadline và time limit là bắt buộc.",
      })
      return
    }

    void createAssignment({
      classId,
      topicId: assignmentDraft.topicId,
      title: assignmentDraft.title.trim(),
      startTime: new Date(assignmentDraft.openAt).toISOString(),
      deadline: new Date(assignmentDraft.deadline).toISOString(),
      timeLimit: Number(assignmentDraft.timeLimit) || 0,
      maxScore: Number(assignmentDraft.score) || 0,
      maxSubmission: Number(assignmentDraft.attemptsAllowed) || 0,
      difficulty: assignmentDraft.difficulty,
      tags: assignmentDraft.tags
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      problem: {
        description: assignmentDraft.description.trim(),
        problemConstraint: assignmentDraft.constraints.trim(),
        starterCodes: assignmentDraft.functionSkeleton.cpp.trim()
          ? { cpp: assignmentDraft.functionSkeleton.cpp }
          : {},
        testcases: assignmentDraft.testCases.map((item) => ({
          input: item.input,
          expectedOutput: item.expectedOutput,
          explanation: item.explanation.trim(),
          hidden: item.hidden,
        })),
      },
    })
      .unwrap()
      .then((createdAssignment) => {
        saveCachedAssignmentProblem(createdAssignment.id, {
          description: assignmentDraft.description.trim(),
          problemConstraint: assignmentDraft.constraints.trim(),
          functionSkeletonCpp: assignmentDraft.functionSkeleton.cpp,
          testcases: assignmentDraft.testCases.map((item) => ({
            input: item.input,
            expectedOutput: item.expectedOutput,
            explanation: item.explanation.trim(),
            hidden: item.hidden,
          })),
          tags: assignmentDraft.tags
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
        })
        resetAssignmentCreateModal()
        toast({
          tone: "success",
          description: "Đã tạo assignment cho section.",
        })
      })
      .catch(() => {
        toast({
          tone: "error",
          description: "Không thể tạo assignment. Kiểm tra lại payload hoặc backend rồi thử lại.",
        })
      })
  }, [assignmentDraft, classId, createAssignment, resetAssignmentCreateModal, toast])

  const handleSaveAssignmentSettings = useCallback(() => {
    if (
      !editingAssignmentId ||
      !assignmentSettingsDraft.title.trim() ||
      !assignmentSettingsDraft.openAt ||
      !assignmentSettingsDraft.deadline
    ) {
      toast({
        tone: "error",
        description: "Tiêu đề, thời điểm mở và hạn nộp là bắt buộc.",
      })
      return
    }

    void updateAssignment({
      classId,
      assignmentId: editingAssignmentId,
      title: assignmentSettingsDraft.title.trim(),
      startTime: new Date(assignmentSettingsDraft.openAt).toISOString(),
      deadline: new Date(assignmentSettingsDraft.deadline).toISOString(),
      timeLimit: Number(assignmentSettingsDraft.timeLimit) || 0,
      maxScore: Number(assignmentSettingsDraft.score) || 0,
      maxSubmission: Number(assignmentSettingsDraft.attemptsAllowed) || 0,
      difficulty: assignmentSettingsDraft.difficulty,
      tags: assignmentSettingsDraft.tags
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    })
      .unwrap()
      .then(() => {
        resetAssignmentEditModal()
        toast({
          tone: "success",
          description: "Đã cập nhật assignment.",
        })
      })
      .catch(() => {
        toast({
          tone: "error",
          description: "Không thể cập nhật assignment. Kiểm tra lại backend rồi thử lại.",
        })
      })
  }, [assignmentSettingsDraft, classId, editingAssignmentId, resetAssignmentEditModal, toast, updateAssignment])

  const handleConfirmDelete = useCallback(() => {
    if (!deleteTarget) {
      return
    }

    const action =
      deleteTarget.type === "class"
        ? deleteClass(deleteTarget.id).unwrap()
        : deleteTarget.type === "topic"
          ? deleteTopic({ classId, topicId: deleteTarget.id }).unwrap()
          : deleteTarget.type === "document"
            ? deleteDocument({ classId, documentId: deleteTarget.id }).unwrap()
            : deleteAssignment({ classId, assignmentId: deleteTarget.id }).unwrap()

    void action
      .then(() => {
        const deletedType = deleteTarget.type
        setDeleteTarget(null)
        toast({
          tone: "success",
          description:
            deletedType === "class"
              ? "Đã xóa lớp học."
              : deletedType === "topic"
                ? "Đã xóa section."
                : deletedType === "document"
                  ? "Đã xóa tài nguyên."
                  : "Đã xóa assignment.",
        })

        if (deletedType === "class") {
          router.push("/lecturer/courses")
        }
      })
      .catch(() => {
        toast({
          tone: "error",
          description: "Không thể xóa dữ liệu. Kiểm tra lại backend rồi thử lại.",
        })
      })
  }, [classId, deleteAssignment, deleteClass, deleteDocument, deleteTarget, deleteTopic, router, toast])

  const handleToggleTopic = useCallback((topicId: string) => {
    setCollapsedTopics((state) => ({
      ...state,
      [topicId]: !state[topicId],
    }))
  }, [])

  const handleAddStudent = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const normalizedUserCode = userCode.trim()
    if (!normalizedUserCode) {
      toast({
        tone: "error",
        description: "Mã sinh viên là bắt buộc.",
      })
      return
    }

    try {
      await addStudentToClass({
        classId,
        userCode: normalizedUserCode,
      }).unwrap()
      setRecentStudentIds((state) =>
        [normalizedUserCode, ...state.filter((id) => id !== normalizedUserCode)].slice(0, 5)
      )
      setUserCode("")
      toast({
        tone: "success",
        description: `Đã thêm sinh viên ${normalizedUserCode} vào lớp.`,
      })
    } catch {
      toast({
        tone: "error",
        description: "Không thể thêm sinh viên vào lớp. Kiểm tra lại mã sinh viên hoặc quyền hiện tại.",
      })
    }
  }

  const handleRemoveStudent = useCallback(
    async (studentUserCode: string) => {
      setRemovingStudentCode(studentUserCode)

      try {
        await removeStudentFromClass({
          classId,
          userCode: studentUserCode,
        }).unwrap()
        setRecentStudentIds((state) => state.filter((item) => item !== studentUserCode))
        toast({
          tone: "success",
          description: `Đã xóa sinh viên ${studentUserCode} khỏi lớp.`,
        })
      } catch {
        toast({
          tone: "error",
          description: "Không thể xóa sinh viên khỏi lớp. Kiểm tra lại quyền hiện tại rồi thử lại.",
        })
      } finally {
        setRemovingStudentCode(null)
      }
    },
    [classId, removeStudentFromClass, toast]
  )

  if (isLoading) {
    return <ClassWorkspaceSkeleton />
  }

  if (error || !bundle || !classroom) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Unable to load class workspace</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Button variant="outline" onClick={() => refetch()}>
            Retry
          </Button>
          <Link href="/lecturer/courses">
            <Button className="bg-[#030391] text-white hover:bg-[#030391]/90">
              Back to classes
            </Button>
          </Link>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <ClassWorkspaceHeader
        classId={classId}
        className={bundle.course.name}
        instructorName={classroom.instructorName}
        enrolledStudentsCount={resolvedEnrolledStudentsCount}
        schedule={classroom.schedule}
        imageUrl={classroom.imageUrl}
        editMode={editMode}
        isRefreshing={
          isFetching ||
          (shouldLoadStudents && isFetchingStudents) ||
          isFetchingTopics ||
          isCreatingTopic ||
          isUpdatingTopic ||
          isDeletingTopic ||
          isCreatingDocument ||
          isUpdatingDocument ||
          isDeletingDocument ||
          isCreatingAssignment ||
          isUpdatingAssignment ||
          isDeletingAssignment ||
          isUpdatingClass ||
          isDeletingClass ||
          isRemovingStudent
        }
        onRefresh={() => {
          void refetch()
          if (shouldLoadStudents) {
            void refetchStudents()
          }
          void refetchTopics()
        }}
        onToggleEditMode={() => setEditMode((value) => !value)}
        onEditClass={openClassModal}
        onDeleteClass={requestDeleteClass}
        onAddSection={handleAddSection}
      />

      <ClassWorkspaceTabs
        activeTab={activeTab}
        hasMountedContent={hasMounted("content")}
        hasMountedStudents={hasMounted("students")}
        editMode={editMode}
        topicCards={topicCards}
        collapsedTopics={collapsedTopics}
        classroom={{
          ...classroom,
          enrolledStudentsCount: resolvedEnrolledStudentsCount,
        }}
        userCode={userCode}
        recentStudentIds={recentStudentIds}
        students={enrolledStudents}
        isAddingStudent={isAddingStudent}
        isLoadingStudents={isLoadingStudents}
        isRemovingStudent={isRemovingStudent}
        removingStudentCode={removingStudentCode}
        formattedCreatedAt={formatClassDate(classroom.createdAt)}
        onTabChange={handleTabChange}
        onToggleTopic={handleToggleTopic}
        onEditTopic={openTopicModal}
        onDeleteTopic={requestDeleteTopic}
        onDeleteMaterial={requestDeleteDocument}
        onOpenResourceModal={openResourceModal}
        onOpenAssignmentModal={openAssignmentCreateModal}
        onEditAssignment={openAssignmentEditModal}
        onDeleteAssignment={requestDeleteAssignment}
        onAddSection={handleAddSection}
        assignmentHrefPrefix="/lecturer/assignments"
        onUserCodeChange={setUserCode}
        onAddStudent={handleAddStudent}
        onRemoveStudent={handleRemoveStudent}
      />

      <ClassWorkspaceModals
        classModalOpen={classModalOpen}
        topicModalOpen={topicModalOpen}
        resourceModalOpen={resourceModalOpen}
        assignmentCreateModalOpen={assignmentCreateModalOpen}
        assignmentEditModalOpen={assignmentEditModalOpen}
        deleteTarget={deleteTarget}
        classDraft={classDraft}
        topicDraft={topicDraft}
        editingTopicId={editingTopicId}
        editingMaterialId={editingMaterialId}
        resourceDraft={resourceDraft}
        assignmentDraft={assignmentDraft}
        assignmentSettingsDraft={assignmentSettingsDraft}
        isSubmittingClass={isUpdatingClass}
        isSubmittingTopic={isCreatingTopic || isUpdatingTopic}
        isSubmittingResource={isCreatingDocument || isUpdatingDocument}
        isSubmittingAssignment={isCreatingAssignment}
        isSubmittingAssignmentSettings={isUpdatingAssignment}
        isDeleting={
          isDeletingClass || isDeletingTopic || isDeletingDocument || isDeletingAssignment
        }
        onCloseClassModal={resetClassModal}
        onCloseTopicModal={resetTopicModal}
        onCloseResourceModal={resetResourceModal}
        onCloseAssignmentCreateModal={resetAssignmentCreateModal}
        onCloseAssignmentEditModal={resetAssignmentEditModal}
        onCloseDeleteModal={() => setDeleteTarget(null)}
        onClassDraftChange={(patch) => {
          if (Object.prototype.hasOwnProperty.call(patch, "description")) {
            setIsClassDescriptionDirty(true)
          }

          setClassDraft((state) => ({ ...state, ...patch }))
        }}
        onTopicDraftChange={(patch) => setTopicDraft((state) => ({ ...state, ...patch }))}
        onResourceDraftChange={(patch) =>
          setResourceDraft((state) => ({ ...state, ...patch }))
        }
        onAssignmentDraftChange={(patch) =>
          setAssignmentDraft((state) => ({ ...state, ...patch }))
        }
        onAssignmentSettingsDraftChange={(patch) =>
          setAssignmentSettingsDraft((state) => ({ ...state, ...patch }))
        }
        onSaveClass={handleSaveClass}
        onSaveTopic={handleSaveTopic}
        onSaveResource={handleSaveMaterial}
        onSaveAssignment={handleSaveAssignment}
        onSaveAssignmentSettings={handleSaveAssignmentSettings}
        onConfirmDelete={handleConfirmDelete}
      />
    </div>
  )
}
