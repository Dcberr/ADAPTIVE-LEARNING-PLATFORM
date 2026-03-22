"use client"

import { useCallback, useMemo, useState } from "react"
import Link from "next/link"
import { ArrowLeft, FilePenLine, Plus } from "lucide-react"

import AssignmentDraftModalForm from "@/components/lms/pages/lecturer-course-detail/AssignmentDraftModalForm"
import ContentTab from "@/components/lms/pages/lecturer-course-detail/ContentTab"
import ResourceModalForm, {
  type ResourceDraft,
} from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"
import StudentsMonitoringTab from "@/components/lms/pages/lecturer-course-detail/StudentsMonitoringTab"
import type {
  AssignmentDraft,
  LecturerCourseBundle,
} from "@/components/lms/pages/lecturer-course-detail/types"
import SimpleModal from "@/components/lms/SimpleModal"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { studentPerformance, type CourseMaterial } from "@/data/lms/extendedMockData"
import { assignments as baseAssignments } from "@/data/lms/mockData"
import { getStudentCourseById } from "@/services/lms/mockLmsService"
import { useAppDispatch, useAppSelector } from "@/store/redux/hooks"
import { lmsActions } from "@/store/redux/slices/lmsSlice"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { EditableTestCase } from "@/components/lms/TestCaseManager"

type LecturerTab = "content" | "students"

const defaultDraftTests: EditableTestCase[] = [
  {
    id: "draft-test-1",
    input: "nums = [2, 7, 11, 15], target = 9",
    expectedOutput: "[0, 1]",
    hidden: false,
  },
  {
    id: "draft-test-2",
    input: "nums = [3, 2, 4], target = 6",
    expectedOutput: "[1, 2]",
    hidden: true,
  },
]

const emptyResourceDraft: ResourceDraft = {
  topicId: "",
  title: "",
  type: "file" as CourseMaterial["type"],
  resourceUrl: "",
  fileSize: "",
  previewLabel: "",
}

const emptyAssignmentDraft: AssignmentDraft = {
  id: "",
  topicId: "",
  title: "",
  description: "",
  difficulty: "Easy",
  score: "100",
  timeLimit: "45 phút",
  openAt: "",
  deadline: "",
  attemptsAllowed: "2",
  constraints: "",
  examples: "",
  topics: "",
  starterCode: {
    python: "def solve(nums, target):\n    pass",
    javascript: "function solve(nums, target) {\n  return []\n}",
    java: "class Solution {\n    public int[] solve(int[] nums, int target) {\n        return new int[]{};\n    }\n}",
    cpp: "#include <vector>\nusing namespace std;\n\nvector<int> solve(vector<int>& nums, int target) {\n    return {};\n}",
  },
  testCases: defaultDraftTests,
}

export default function LecturerCourseDetailPage({ courseId }: { courseId: string }) {
  const [editMode, setEditMode] = useState(false)
  const [collapsedTopics, setCollapsedTopics] = useState<Record<string, boolean>>({})
  const [assignmentDrafts, setAssignmentDrafts] = useState<AssignmentDraft[]>([])
  const [resourceModalOpen, setResourceModalOpen] = useState(false)
  const [assignmentModalOpen, setAssignmentModalOpen] = useState(false)
  const [editingMaterialId, setEditingMaterialId] = useState<string | null>(null)
  const [editingDraftId, setEditingDraftId] = useState<string | null>(null)
  const [resourceDraft, setResourceDraft] = useState(emptyResourceDraft)
  const [assignmentDraft, setAssignmentDraft] = useState(emptyAssignmentDraft)
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<LecturerTab>("content")
  const dispatch = useAppDispatch()
  const topicsState = useAppSelector((state) => state.lms.topics)
  const materialsState = useAppSelector((state) => state.lms.materials)

  const course = getStudentCourseById(courseId)
  const bundle = useMemo<LecturerCourseBundle | null>(() => {
    if (!course) {
      return null
    }

    const topics = topicsState
      .filter((topic) => topic.courseId === courseId)
      .sort((left, right) => left.order - right.order)
      .map((topic) => ({
        ...topic,
        materials: materialsState.filter((material) => material.topicId === topic.id),
        assignments: baseAssignments.filter((assignment) => topic.assignmentIds.includes(assignment.id)),
      }))

    return {
      course,
      topics,
      students: studentPerformance.filter((student) => student.courseId === courseId),
      assignments: baseAssignments.filter((assignment) => assignment.courseId === courseId),
    }
  }, [course, courseId, materialsState, topicsState])

  const topicCards = useMemo(
    () =>
      bundle?.topics.map((topic) => ({
        ...topic,
        customAssignments: assignmentDrafts.filter((item) => item.topicId === topic.id),
      })) ?? [],
    [assignmentDrafts, bundle]
  )
  const topicCount = bundle?.topics.length ?? 0

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

  const openResourceModal = useCallback((topicId: string, materialId?: string) => {
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
  }, [topicCards])

  const openAssignmentModal = useCallback((topicId: string, draft?: AssignmentDraft) => {
    setEditingDraftId(draft?.id ?? null)
    setAssignmentDraft(
      draft
        ? draft
        : {
            ...emptyAssignmentDraft,
            topicId,
          }
    )
    setAssignmentModalOpen(true)
  }, [])

  const handleAddSection = useCallback(() => {
    dispatch(lmsActions.addTopic({
      courseId,
      title: `New section ${topicCount + 1}`,
      summary: "Mô tả nội dung học phần cho section này.",
    }))
  }, [courseId, dispatch, topicCount])

  const handleSaveMaterial = useCallback(() => {
    if (!resourceDraft.title.trim()) {
      return
    }

    if (editingMaterialId) {
      dispatch(lmsActions.updateMaterial({ id: editingMaterialId, patch: resourceDraft }))
    } else {
      dispatch(lmsActions.addMaterial({
        ...resourceDraft,
        uploadedAt: new Date().toISOString(),
      }))
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

    setAssignmentDrafts((state) => {
      if (editingDraftId) {
        return state.map((item) => (item.id === editingDraftId ? nextDraft : item))
      }

      return [nextDraft, ...state]
    })

    resetAssignmentModal()
  }, [assignmentDraft, editingDraftId])

  const handleToggleTopic = useCallback((topicId: string) => {
    setCollapsedTopics((state) => ({
      ...state,
      [topicId]: !state[topicId],
    }))
  }, [])

  const handleUpdateTopic = useCallback(
    (topicId: string, patch: { title?: string; summary?: string }) => {
      dispatch(lmsActions.updateTopic({ id: topicId, patch }))
    },
    [dispatch]
  )

  const handleDeleteTopic = useCallback(
    (topicId: string) => {
      dispatch(lmsActions.deleteTopic(topicId))
    },
    [dispatch]
  )

  const handleDeleteMaterial = useCallback(
    (materialId: string) => {
      dispatch(lmsActions.deleteMaterial(materialId))
    },
    [dispatch]
  )

  const handleDeleteDraftAssignment = useCallback((draftId: string) => {
    setAssignmentDrafts((state) => state.filter((item) => item.id !== draftId))
  }, [])

  if (!bundle) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading course workspace...</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link href="/lecturer/courses">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 size-4" /> Back to Courses
          </Button>
        </Link>
        <div className="flex gap-3">
          <Button
            variant={editMode ? "default" : "outline"}
            className="rounded-2xl"
            onClick={() => setEditMode((value) => !value)}
          >
            <FilePenLine className="size-4" />
            {editMode ? "Thoát chỉnh sửa" : "Chỉnh sửa nội dung"}
          </Button>
          {editMode ? (
            <Button
              className="rounded-2xl bg-[#1488D8] text-white hover:bg-[#1488D8]/90"
              onClick={handleAddSection}
            >
              <Plus className="size-4" />
              Add section
            </Button>
          ) : null}
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center gap-2">
            <Badge className={`${bundle.course.color} text-white`}>{bundle.course.code}</Badge>
            <CardTitle className="text-2xl text-[#030391]">{bundle.course.name}</CardTitle>
          </div>
          <p className="text-sm text-slate-600">{bundle.course.description}</p>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={(value) => handleTabChange(value as LecturerTab)}>
        <TabsList>
          <TabsTrigger value="content">Nội dung khóa học</TabsTrigger>
          <TabsTrigger value="students">Sinh viên</TabsTrigger>
        </TabsList>

        <TabsContent
          value="content"
          forceMount={hasMounted("content") ? true : undefined}
          hidden={activeTab !== "content"}
        >
          <ContentTab
            topicCards={topicCards}
            editMode={editMode}
            collapsedTopics={collapsedTopics}
            onToggleTopic={handleToggleTopic}
            onUpdateTopic={handleUpdateTopic}
            onDeleteTopic={handleDeleteTopic}
            onDeleteMaterial={handleDeleteMaterial}
            onOpenResourceModal={openResourceModal}
            onOpenAssignmentModal={openAssignmentModal}
            onDeleteDraftAssignment={handleDeleteDraftAssignment}
            onAddSection={handleAddSection}
          />
        </TabsContent>

        <TabsContent
          value="students"
          forceMount={hasMounted("students") ? true : undefined}
          hidden={activeTab !== "students"}
          className="mt-6"
        >
          <StudentsMonitoringTab students={bundle.students} />
        </TabsContent>
      </Tabs>

      <SimpleModal
        open={resourceModalOpen}
        title={editingMaterialId ? "Chỉnh sửa tài nguyên" : "Thêm tài nguyên"}
        description="Nhập thông tin file, video hoặc image resource cho section hiện tại."
        onClose={resetResourceModal}
      >
        <ResourceModalForm
          draft={resourceDraft}
          onChange={(patch) => setResourceDraft((state) => ({ ...state, ...patch }))}
          onCancel={resetResourceModal}
          onSave={handleSaveMaterial}
        />
      </SimpleModal>

      <SimpleModal
        open={assignmentModalOpen}
        title={editingDraftId ? "Chỉnh sửa assignment" : "Thêm assignment"}
        description="Popup này mô phỏng form tạo assignment như bên LMS."
        onClose={resetAssignmentModal}
      >
        <AssignmentDraftModalForm
          draft={assignmentDraft}
          onChange={(patch) => setAssignmentDraft((state) => ({ ...state, ...patch }))}
          onCancel={resetAssignmentModal}
          onSave={handleSaveAssignmentDraft}
        />
      </SimpleModal>
    </div>
  )
}
