"use client"

import type { FormEvent } from "react"

import ContentTab from "@/components/lms/pages/lecturer-course-detail/ContentTab"
import StudentEnrollmentCard from "@/components/lms/pages/lecturer-course-detail/StudentEnrollmentCard"
import StudentsMonitoringTab from "@/components/lms/pages/lecturer-course-detail/StudentsMonitoringTab"
import type {
  AssignmentDraft,
  TopicCard,
} from "@/components/lms/pages/lecturer-course-detail/types"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { StudentPerformanceRecord } from "@/data/lms/extendedMockData"

type FeedbackState =
  | {
      tone: "success" | "error"
      message: string
    }
  | null

export default function ClassWorkspaceTabs({
  activeTab,
  hasMountedContent,
  hasMountedStudents,
  editMode,
  topicCards,
  collapsedTopics,
  contentFeedback,
  classroom,
  studentId,
  feedback,
  recentStudentIds,
  students,
  isAddingStudent,
  formattedCreatedAt,
  onTabChange,
  onToggleTopic,
  onUpdateTopic,
  onDeleteTopic,
  onDeleteMaterial,
  onOpenResourceModal,
  onOpenAssignmentModal,
  onDeleteDraftAssignment,
  onAddSection,
  onStudentIdChange,
  onAddStudent,
  assignmentHrefPrefix,
}: {
  activeTab: "content" | "students"
  hasMountedContent: boolean
  hasMountedStudents: boolean
  editMode: boolean
  topicCards: TopicCard[]
  collapsedTopics: Record<string, boolean>
  contentFeedback: FeedbackState
  classroom: {
    instructorName: string
    enrolledStudentsCount: number
    schedule: string | null
  }
  studentId: string
  feedback: FeedbackState
  recentStudentIds: string[]
  students: StudentPerformanceRecord[]
  isAddingStudent: boolean
  formattedCreatedAt: string
  onTabChange: (value: "content" | "students") => void
  onToggleTopic: (topicId: string) => void
  onUpdateTopic: (topicId: string, patch: { title?: string; summary?: string }) => void
  onDeleteTopic: (topicId: string) => void
  onDeleteMaterial: (materialId: string) => void
  onOpenResourceModal: (topicId: string, materialId?: string) => void
  onOpenAssignmentModal: (topicId: string, draft?: AssignmentDraft) => void
  onDeleteDraftAssignment: (draftId: string) => void
  onAddSection: () => void
  onStudentIdChange: (value: string) => void
  onAddStudent: (event: FormEvent<HTMLFormElement>) => void
  assignmentHrefPrefix?: string
}) {
  return (
    <Tabs value={activeTab} onValueChange={(value) => onTabChange(value as "content" | "students")}>
      <TabsList>
        <TabsTrigger value="content">Nội dung khóa học</TabsTrigger>
        <TabsTrigger value="students">Sinh viên</TabsTrigger>
      </TabsList>

      <TabsContent
        value="content"
        forceMount={hasMountedContent ? true : undefined}
        hidden={activeTab !== "content"}
      >
        <ContentTab
          topicCards={topicCards}
          editMode={editMode}
          feedback={contentFeedback}
          collapsedTopics={collapsedTopics}
          onToggleTopic={onToggleTopic}
          onUpdateTopic={onUpdateTopic}
          onDeleteTopic={onDeleteTopic}
          onDeleteMaterial={onDeleteMaterial}
          onOpenResourceModal={onOpenResourceModal}
          onOpenAssignmentModal={onOpenAssignmentModal}
          onDeleteDraftAssignment={onDeleteDraftAssignment}
          onAddSection={onAddSection}
          assignmentHrefPrefix={assignmentHrefPrefix}
        />
      </TabsContent>

      <TabsContent
        value="students"
        forceMount={hasMountedStudents ? true : undefined}
        hidden={activeTab !== "students"}
        className="mt-6 space-y-6"
      >
        <StudentEnrollmentCard
          instructorName={classroom.instructorName}
          enrolledStudentsCount={classroom.enrolledStudentsCount}
          createdAt={formattedCreatedAt}
          schedule={classroom.schedule}
          studentId={studentId}
          feedback={feedback}
          recentStudentIds={recentStudentIds}
          isSubmitting={isAddingStudent}
          onStudentIdChange={onStudentIdChange}
          onSubmit={onAddStudent}
        />
        <StudentsMonitoringTab students={students} />
      </TabsContent>
    </Tabs>
  )
}
