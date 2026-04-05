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
  getClassStatusClassName,
} from "@/components/lms/pages/lecturer-course-detail/constants"
import { type ResourceDraft } from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"
import type {
  AssignmentDraft,
  LecturerCourseBundle,
} from "@/components/lms/pages/lecturer-course-detail/types"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { studentPerformance } from "@/data/lms/extendedMockData"
import { assignments as baseAssignments } from "@/data/lms/mockData"
import {
  useAddStudentToClassMutation,
  useGetClassByIdQuery,
} from "@/store/redux/api/lmsApi"
import { useAppDispatch, useAppSelector } from "@/store/redux/hooks"
import { lmsActions } from "@/store/redux/slices/lmsSlice"
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
  const [assignmentDrafts, setAssignmentDrafts] = useState<AssignmentDraft[]>([])
  const [resourceModalOpen, setResourceModalOpen] = useState(false)
  const [assignmentModalOpen, setAssignmentModalOpen] = useState(false)
  const [editingMaterialId, setEditingMaterialId] = useState<string | null>(null)
  const [editingDraftId, setEditingDraftId] = useState<string | null>(null)
  const [resourceDraft, setResourceDraft] = useState<ResourceDraft>(emptyResourceDraft)
  const [assignmentDraft, setAssignmentDraft] = useState(emptyAssignmentDraft)
  const [studentId, setStudentId] = useState("")
  const [feedback, setFeedback] = useState<FeedbackState>(null)
  const [recentStudentIds, setRecentStudentIds] = useState<string[]>([])
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<LecturerTab>("content")
  const dispatch = useAppDispatch()
  const topicsState = useAppSelector((state) => state.lms.topics)
  const materialsState = useAppSelector((state) => state.lms.materials)
  const {
    data: classroom,
    error,
    isFetching,
    isLoading,
    refetch,
  } = useGetClassByIdQuery(classId)
  const [addStudentToClass, { isLoading: isAddingStudent }] = useAddStudentToClassMutation()

  const bundle = useMemo<LecturerCourseBundle | null>(() => {
    if (!classroom) {
      return null
    }

    const topics = topicsState
      .filter((topic) => topic.courseId === classId)
      .sort((left, right) => left.order - right.order)
      .map((topic) => ({
        ...topic,
        materials: materialsState.filter((material) => material.topicId === topic.id),
        assignments: baseAssignments.filter((assignment) =>
          topic.assignmentIds.includes(assignment.id)
        ),
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
      assignments: baseAssignments.filter((assignment) => assignment.courseId === classId),
    }
  }, [classId, classroom, materialsState, topicsState])

  const topicCards = useMemo(
    () =>
      bundle?.topics.map((topic) => ({
        ...topic,
        customAssignments: assignmentDrafts.filter((item) => item.topicId === topic.id),
      })) ?? [],
    [assignmentDrafts, bundle]
  )

  const resetResourceModal = () => {
    setResourceModalOpen(false)
    setEditingMaterialId(null)
    setResourceDraft(emptyResourceDraft)
  }

  const resetAssignmentModal = () => {
    setAssignmentModalOpen(false)
    setEditingDraftId(null)
    setAssignmentDraft(emptyAssignmentDraft)
  }

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
              type: material.type,
              resourceUrl: material.resourceUrl,
              fileSize: material.fileSize,
              previewLabel: material.previewLabel,
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
    dispatch(
      lmsActions.addTopic({
        courseId: classId,
        title: `New section ${topicCards.length + 1}`,
        summary: "Mô tả nội dung học phần cho section này.",
      })
    )
  }, [classId, dispatch, topicCards.length])

  const handleSaveMaterial = useCallback(() => {
    if (!resourceDraft.title.trim()) {
      return
    }

    if (editingMaterialId) {
      dispatch(lmsActions.updateMaterial({ id: editingMaterialId, patch: resourceDraft }))
    } else {
      dispatch(
        lmsActions.addMaterial({
          ...resourceDraft,
          uploadedAt: new Date().toISOString(),
        })
      )
    }

    resetResourceModal()
  }, [dispatch, editingMaterialId, resourceDraft])

  const handleSaveAssignmentDraft = useCallback(() => {
    if (!assignmentDraft.title.trim()) {
      return
    }

    const nextDraft: AssignmentDraft = {
      ...assignmentDraft,
      id: editingDraftId ?? `draft-${Date.now()}`,
    }

    setAssignmentDrafts((state) =>
      editingDraftId
        ? state.map((item) => (item.id === editingDraftId ? nextDraft : item))
        : [nextDraft, ...state]
    )

    resetAssignmentModal()
  }, [assignmentDraft, editingDraftId])

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
        className={bundle.course.name}
        classDescription={bundle.course.description}
        classStatus={classroom.status}
        statusClassName={getClassStatusClassName(classroom.status)}
        editMode={editMode}
        isRefreshing={isFetching}
        onRefresh={refetch}
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
        classroom={classroom}
        studentId={studentId}
        feedback={feedback}
        recentStudentIds={recentStudentIds}
        students={bundle.students}
        isAddingStudent={isAddingStudent}
        formattedCreatedAt={formatClassDate(classroom.createdAt)}
        onTabChange={handleTabChange}
        onToggleTopic={handleToggleTopic}
        onUpdateTopic={(topicId, patch) => dispatch(lmsActions.updateTopic({ id: topicId, patch }))}
        onDeleteTopic={(topicId) => dispatch(lmsActions.deleteTopic(topicId))}
        onDeleteMaterial={(materialId) => dispatch(lmsActions.deleteMaterial(materialId))}
        onOpenResourceModal={openResourceModal}
        onOpenAssignmentModal={openAssignmentModal}
        onDeleteDraftAssignment={(draftId) =>
          setAssignmentDrafts((state) => state.filter((item) => item.id !== draftId))
        }
        onAddSection={handleAddSection}
        onStudentIdChange={setStudentId}
        onAddStudent={handleAddStudent}
      />

      <ClassWorkspaceModals
        resourceModalOpen={resourceModalOpen}
        assignmentModalOpen={assignmentModalOpen}
        editingMaterialId={editingMaterialId}
        editingDraftId={editingDraftId}
        resourceDraft={resourceDraft}
        assignmentDraft={assignmentDraft}
        onCloseResourceModal={resetResourceModal}
        onCloseAssignmentModal={resetAssignmentModal}
        onResourceDraftChange={(patch) => setResourceDraft((state) => ({ ...state, ...patch }))}
        onAssignmentDraftChange={(patch) =>
          setAssignmentDraft((state) => ({ ...state, ...patch }))
        }
        onSaveResource={handleSaveMaterial}
        onSaveAssignment={handleSaveAssignmentDraft}
      />
    </div>
  )
}
