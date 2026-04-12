import type { StudentPerformanceRecord } from "@/data/lms/extendedMockData"
import type { EditableTestCase } from "@/components/lms/TestCaseManager"

export type TopicMaterial = {
  id: string
  title: string
  description: string
  resourceUrl: string
  type: "file" | "video" | "image"
  fileSize: string
  previewLabel: string
}

export type TopicAssignment = {
  id: string
  title: string
  deadline: string
  startTime?: string | null
  timeLimit?: number | null
  maxScore?: number | null
  maxSubmission?: number | null
  tags?: string[] | null
  difficulty: string
  status: string
}

export type TopicBundle = {
  id: string
  courseId: string
  order: number
  title: string
  summary: string
  materials: TopicMaterial[]
  assignments: TopicAssignment[]
}

export type AssignmentDraft = {
  id: string
  topicId: string
  title: string
  description: string
  difficulty: "EASY" | "MEDIUM" | "HARD"
  score: string
  timeLimit: string
  openAt: string
  deadline: string
  attemptsAllowed: string
  constraints: string
  tags: string
  starterCode: {
    cpp: string
  }
  testCases: EditableTestCase[]
}

export type TopicCard = TopicBundle & {
  customAssignments: AssignmentDraft[]
}

export type LecturerCourseBundle = {
  course: {
    id: string
    code: string
    name: string
    description: string
    color: string
  }
  topics: TopicBundle[]
  students: StudentPerformanceRecord[]
  assignments: TopicAssignment[]
}
