"use client"

import { useCallback, useMemo, useState, type FormEvent } from "react"
import Link from "next/link"

import ClassWorkspaceHeader from "@/components/lms/pages/lecturer-course-detail/ClassWorkspaceHeader"
import ClassWorkspaceModals from "@/components/lms/pages/lecturer-course-detail/ClassWorkspaceModals"
import ClassWorkspaceTabs from "@/components/lms/pages/lecturer-course-detail/ClassWorkspaceTabs"
import {
  emptyAssignmentDraft,
  emptyResourceDraft,
  formatClassDate,
} from "@/components/lms/pages/lecturer-course-detail/constants"
import { type ResourceDraft } from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"
import { type TopicDraft } from "@/components/lms/pages/lecturer-course-detail/TopicModalForm"
import type {
  AssignmentDraft,
  LecturerCourseBundle,
} from "@/components/lms/pages/lecturer-course-detail/types"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { studentPerformance } from "@/data/lms/extendedMockData"
import { getBackendBaseUrl } from "@/lib/auth"
import { saveCachedAssignmentProblem } from "@/lib/assignment-problem-cache"
import {
  useAddStudentToClassMutation,
  useCreateAssignmentMutation,
  useCreateDocumentMutation,
  useCreateTopicMutation,
  useGetClassByIdQuery,
  useGetClassTopicsQuery,
} from "@/store/redux/api/lmsApi"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type LecturerTab = "content" | "students"
type FeedbackState =
  | {
      tone: "success" | "error"
      message: string
    }
  | null

export default function LecturerCourseDetailPage({ classId }: { classId: string }) {
  const [editMode, setEditMode] = useState(false)
  const [collapsedTopics, setCollapsedTopics] = useState<Record<string, boolean>>({})
  const [topicDrafts, setTopicDrafts] = useState<
    Record<string, { title?: string; summary?: string }>
  >({})
  const [topicModalOpen, setTopicModalOpen] = useState(false)
  const [assignmentDrafts, setAssignmentDrafts] = useState<AssignmentDraft[]>([])
  const [resourceModalOpen, setResourceModalOpen] = useState(false)
  const [assignmentModalOpen, setAssignmentModalOpen] = useState(false)
  const [editingMaterialId, setEditingMaterialId] = useState<string | null>(null)
  const [editingDraftId, setEditingDraftId] = useState<string | null>(null)
  const [topicDraft, setTopicDraft] = useState<TopicDraft>({ title: "", description: "" })
  const [resourceDraft, setResourceDraft] = useState<ResourceDraft>(emptyResourceDraft)
  const [assignmentDraft, setAssignmentDraft] = useState(emptyAssignmentDraft)
  const [studentId, setStudentId] = useState("")
  const [feedback, setFeedback] = useState<FeedbackState>(null)
  const [contentFeedback, setContentFeedback] = useState<FeedbackState>(null)
  const [recentStudentIds, setRecentStudentIds] = useState<string[]>([])
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<LecturerTab>("content")
  const {
    data: classroom,
    error,
    isFetching,
    isLoading,
    refetch,
  } = useGetClassByIdQuery(classId)
  const {
    data: topicDetails = [],
    isFetching: isFetchingTopics,
    refetch: refetchTopics,
  } = useGetClassTopicsQuery(classId)
  const [addStudentToClass, { isLoading: isAddingStudent }] = useAddStudentToClassMutation()
  const [createDocument, { isLoading: isCreatingDocument }] = useCreateDocumentMutation()
  const [createAssignment, { isLoading: isCreatingAssignment }] = useCreateAssignmentMutation()
  const [createTopic, { isLoading: isCreatingTopic }] = useCreateTopicMutation()
  const backendBaseUrl = getBackendBaseUrl()

  const bundle = useMemo<LecturerCourseBundle | null>(() => {
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
      title: topicDrafts[topic.id]?.title ?? topic.title,
      summary: topicDrafts[topic.id]?.summary ?? topic.description,
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
        difficulty: assignment.difficulty,
        status: assignment.status,
      })),
    }))

    return {
      course: {
        id: classId,
        code: classroom.status,
        name: classroom.name,
        description: `Instructor ${classroom.instructorName} • ${classroom.enrolledStudentsCount} students • ${
          classroom.schedule ?? "Schedule chưa cấu hình"
        } • Created ${formatClassDate(classroom.createdAt)}`,
        color: "bg-[#030391]",
      },
      topics,
      students: studentPerformance.filter((student) => student.courseId === classId),
      assignments: topics.flatMap((topic) => topic.assignments),
    }
  }, [backendBaseUrl, classId, classroom, topicDetails, topicDrafts])

  const topicCards = useMemo(
    () =>
      bundle?.topics.map((topic) => ({
        ...topic,
        customAssignments: assignmentDrafts.filter((item) => item.topicId === topic.id),
      })) ?? [],
    [assignmentDrafts, bundle]
  )

  const resetResourceModal = useCallback(() => {
    setResourceModalOpen(false)
    setEditingMaterialId(null)
    setResourceDraft(emptyResourceDraft)
  }, [])

  const resetTopicModal = useCallback(() => {
    setTopicModalOpen(false)
    setTopicDraft({ title: "", description: "" })
  }, [])

  const resetAssignmentModal = useCallback(() => {
    setAssignmentModalOpen(false)
    setEditingDraftId(null)
    setAssignmentDraft(emptyAssignmentDraft)
  }, [])

  const openResourceModal = useCallback(
    (topicId: string, materialId?: string) => {
      const material = topicCards
        .flatMap((topic) => topic.materials)
        .find((item) => item.id === materialId)

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

  const openAssignmentModal = useCallback((topicId: string, draft?: AssignmentDraft) => {
    setEditingDraftId(draft?.id ?? null)
    setAssignmentDraft(draft ? draft : { ...emptyAssignmentDraft, topicId })
    setAssignmentModalOpen(true)
  }, [])

  const handleAddSection = useCallback(() => {
    setTopicModalOpen(true)
  }, [])

  const handleSaveTopic = useCallback(() => {
    const title = topicDraft.title.trim()
    const description = topicDraft.description.trim()

    if (!title || !description) {
      setContentFeedback({
        tone: "error",
        message: "Tên section và mô tả là bắt buộc.",
      })
      return
    }

    void createTopic({
      classId,
      title,
      description,
    })
      .unwrap()
      .then(() => {
        resetTopicModal()
        setContentFeedback({
          tone: "success",
          message: "Đã thêm section mới cho lớp học.",
        })
      })
      .catch(() => {
        setContentFeedback({
          tone: "error",
          message: "Không thể tạo topic mới. Kiểm tra lại backend rồi thử lại.",
        })
      })
  }, [classId, createTopic, resetTopicModal, topicDraft])

  const handleSaveMaterial = useCallback(() => {
    if (editingMaterialId) {
      setContentFeedback({
        tone: "error",
        message: "Chưa tích hợp API chỉnh sửa tài nguyên ở màn hình này.",
      })
      return
    }

    const title = resourceDraft.title.trim()
    const description = resourceDraft.description.trim()
    const file = resourceDraft.file

    if (!resourceDraft.topicId || !title || !description || !file) {
      setContentFeedback({
        tone: "error",
        message: "Tên tài nguyên, mô tả và file upload là bắt buộc.",
      })
      return
    }

    void createDocument({
      topicId: resourceDraft.topicId,
      title,
      description,
      file,
    })
      .unwrap()
      .then(() => {
        resetResourceModal()
        setContentFeedback({
          tone: "success",
          message: "Đã thêm tài nguyên cho section.",
        })
      })
      .catch(() => {
        setContentFeedback({
          tone: "error",
          message: "Không thể upload tài nguyên. Kiểm tra lại backend rồi thử lại.",
        })
      })
  }, [createDocument, editingMaterialId, resetResourceModal, resourceDraft])

  const handleSaveAssignmentDraft = useCallback(() => {
    if (editingDraftId) {
      setContentFeedback({
        tone: "error",
        message: "Chưa tích hợp API chỉnh sửa assignment ở màn hình này.",
      })
      return
    }

    if (
      !assignmentDraft.title.trim() ||
      !assignmentDraft.description.trim() ||
      !assignmentDraft.openAt ||
      !assignmentDraft.deadline ||
      !assignmentDraft.timeLimit
    ) {
      setContentFeedback({
        tone: "error",
        message: "Tiêu đề, mô tả, thời điểm mở, deadline và time limit là bắt buộc.",
      })
      return
    }

    void createAssignment({
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
      description: assignmentDraft.description.trim(),
      problemConstraint: assignmentDraft.constraints.trim(),
      starterCodes: assignmentDraft.starterCode.cpp.trim()
        ? { cpp: assignmentDraft.starterCode.cpp }
        : {},
      testcases: assignmentDraft.testCases.map((item) => ({
        input: item.input,
        expectedOutput: item.expectedOutput,
        explanation: item.explanation.trim(),
        hidden: item.hidden,
      })),
    })
      .unwrap()
      .then((createdAssignment) => {
        saveCachedAssignmentProblem(createdAssignment.id, {
          description: assignmentDraft.description.trim(),
          problemConstraint: assignmentDraft.constraints.trim(),
          starterCodeCpp: assignmentDraft.starterCode.cpp,
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
        resetAssignmentModal()
        setContentFeedback({
          tone: "success",
          message: "Đã tạo assignment cho section.",
        })
      })
      .catch(() => {
        setContentFeedback({
          tone: "error",
          message: "Không thể tạo assignment. Kiểm tra lại payload hoặc backend rồi thử lại.",
        })
      })
  }, [assignmentDraft, createAssignment, editingDraftId, resetAssignmentModal])

  const handleToggleTopic = useCallback((topicId: string) => {
    setCollapsedTopics((state) => ({
      ...state,
      [topicId]: !state[topicId],
    }))
  }, [])

  const handleAddStudent = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const normalizedStudentId = studentId.trim()
    if (!normalizedStudentId) {
      setFeedback({
        tone: "error",
        message: "Student ID là bắt buộc.",
      })
      return
    }

    try {
      await addStudentToClass({
        classId,
        studentId: normalizedStudentId,
      }).unwrap()
      setRecentStudentIds((state) =>
        [normalizedStudentId, ...state.filter((id) => id !== normalizedStudentId)].slice(0, 5)
      )
      setStudentId("")
      setFeedback({
        tone: "success",
        message: `Đã thêm student ${normalizedStudentId} vào lớp.`,
      })
    } catch {
      setFeedback({
        tone: "error",
        message: "Không thể thêm học sinh vào lớp. Kiểm tra lại student ID hoặc quyền hiện tại.",
      })
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading class workspace...</CardTitle>
        </CardHeader>
      </Card>
    )
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
        enrolledStudentsCount={classroom.enrolledStudentsCount}
        schedule={classroom.schedule}
        imageUrl={classroom.imageUrl}
        editMode={editMode}
        isRefreshing={
          isFetching ||
          isFetchingTopics ||
          isCreatingTopic ||
          isCreatingDocument ||
          isCreatingAssignment
        }
        onRefresh={() => {
          void refetch()
          void refetchTopics()
        }}
        onToggleEditMode={() => setEditMode((value) => !value)}
        onAddSection={handleAddSection}
      />

      <ClassWorkspaceTabs
        activeTab={activeTab}
        hasMountedContent={hasMounted("content")}
        hasMountedStudents={hasMounted("students")}
        editMode={editMode}
        topicCards={topicCards}
        collapsedTopics={collapsedTopics}
        contentFeedback={contentFeedback}
        classroom={classroom}
        studentId={studentId}
        feedback={feedback}
        recentStudentIds={recentStudentIds}
        students={bundle.students}
        isAddingStudent={isAddingStudent}
        formattedCreatedAt={formatClassDate(classroom.createdAt)}
        onTabChange={handleTabChange}
        onToggleTopic={handleToggleTopic}
        onUpdateTopic={(topicId, patch) =>
          setTopicDrafts((state) => ({
            ...state,
            [topicId]: {
              ...state[topicId],
              ...patch,
            },
          }))
        }
        onDeleteTopic={() =>
          setContentFeedback({
            tone: "error",
            message: "Chưa tích hợp API xóa topic ở màn hình này.",
          })
        }
        onDeleteMaterial={() =>
          setContentFeedback({
            tone: "error",
            message: "Chưa tích hợp API chỉnh sửa tài nguyên ở màn hình này.",
          })
        }
        onOpenResourceModal={openResourceModal}
        onOpenAssignmentModal={openAssignmentModal}
        onDeleteDraftAssignment={(draftId) =>
          setAssignmentDrafts((state) => state.filter((item) => item.id !== draftId))
        }
        onAddSection={handleAddSection}
        assignmentHrefPrefix="/lecturer/assignments"
        onStudentIdChange={setStudentId}
        onAddStudent={handleAddStudent}
      />

      <ClassWorkspaceModals
        topicModalOpen={topicModalOpen}
        resourceModalOpen={resourceModalOpen}
        assignmentModalOpen={assignmentModalOpen}
        topicDraft={topicDraft}
        editingMaterialId={editingMaterialId}
        editingDraftId={editingDraftId}
        resourceDraft={resourceDraft}
        assignmentDraft={assignmentDraft}
        isSubmittingTopic={isCreatingTopic}
        isSubmittingResource={isCreatingDocument}
        isSubmittingAssignment={isCreatingAssignment}
        onCloseTopicModal={resetTopicModal}
        onCloseResourceModal={resetResourceModal}
        onCloseAssignmentModal={resetAssignmentModal}
        onTopicDraftChange={(patch) => setTopicDraft((state) => ({ ...state, ...patch }))}
        onResourceDraftChange={(patch) => setResourceDraft((state) => ({ ...state, ...patch }))}
        onAssignmentDraftChange={(patch) =>
          setAssignmentDraft((state) => ({ ...state, ...patch }))
        }
        onSaveTopic={handleSaveTopic}
        onSaveResource={handleSaveMaterial}
        onSaveAssignment={handleSaveAssignmentDraft}
      />
    </div>
  )
}
