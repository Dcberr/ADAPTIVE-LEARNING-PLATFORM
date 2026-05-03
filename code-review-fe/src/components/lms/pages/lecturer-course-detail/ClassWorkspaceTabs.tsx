"use client"

import type { FormEvent } from "react"

import ContentTab from "@/components/lms/pages/lecturer-course-detail/ContentTab"
import StudentEnrollmentCard from "@/components/lms/pages/lecturer-course-detail/StudentEnrollmentCard"
import StudentsMonitoringTab from "@/components/lms/pages/lecturer-course-detail/StudentsMonitoringTab"
import type { TopicCard } from "@/components/lms/pages/lecturer-course-detail/types"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { ClassStudent } from "@/store/redux/api/lmsApi"

export default function ClassWorkspaceTabs({
  activeTab,
  hasMountedContent,
  hasMountedStudents,
  editMode,
  topicCards,
  collapsedTopics,
  classroom,
  userCode,
  recentStudentIds,
  students,
  isAddingStudent,
  isLoadingStudents,
  isRemovingStudent,
  removingStudentCode,
  formattedCreatedAt,
  onTabChange,
  onToggleTopic,
  onEditTopic,
  onDeleteTopic,
  onDeleteMaterial,
  onOpenResourceModal,
  onOpenAssignmentModal,
  onEditAssignment,
  onDeleteAssignment,
  onAddSection,
  onUserCodeChange,
  onAddStudent,
  onRemoveStudent,
  assignmentHrefPrefix,
}: {
  activeTab: "content" | "students"
  hasMountedContent: boolean
  hasMountedStudents: boolean
  editMode: boolean
  topicCards: TopicCard[]
  collapsedTopics: Record<string, boolean>
  classroom: {
    instructorName: string
    enrolledStudentsCount: number
    schedule: string | null
  }
  userCode: string
  recentStudentIds: string[]
  students: ClassStudent[]
  isAddingStudent: boolean
  isLoadingStudents: boolean
  isRemovingStudent: boolean
  removingStudentCode: string | null
  formattedCreatedAt: string
  onTabChange: (value: "content" | "students") => void
  onToggleTopic: (topicId: string) => void
  onEditTopic: (topicId: string) => void
  onDeleteTopic: (topicId: string) => void
  onDeleteMaterial: (materialId: string) => void
  onOpenResourceModal: (topicId: string, materialId?: string) => void
  onOpenAssignmentModal: (topicId: string) => void
  onEditAssignment: (assignmentId: string) => void
  onDeleteAssignment: (assignmentId: string) => void
  onAddSection: () => void
  onUserCodeChange: (value: string) => void
  onAddStudent: (event: FormEvent<HTMLFormElement>) => void
  onRemoveStudent: (userCode: string) => Promise<void>
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
          collapsedTopics={collapsedTopics}
          onToggleTopic={onToggleTopic}
          onEditTopic={onEditTopic}
          onDeleteTopic={onDeleteTopic}
          onDeleteMaterial={onDeleteMaterial}
          onOpenResourceModal={onOpenResourceModal}
          onOpenAssignmentModal={onOpenAssignmentModal}
          onEditAssignment={onEditAssignment}
          onDeleteAssignment={onDeleteAssignment}
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
          userCode={userCode}
          recentStudentIds={recentStudentIds}
          isSubmitting={isAddingStudent}
          onUserCodeChange={onUserCodeChange}
          onSubmit={onAddStudent}
        />
        <StudentsMonitoringTab
          students={students}
          isLoading={isLoadingStudents}
          isRemovingStudent={isRemovingStudent}
          removingStudentCode={removingStudentCode}
          onRemoveStudent={onRemoveStudent}
        />
      </TabsContent>
    </Tabs>
  )
}
