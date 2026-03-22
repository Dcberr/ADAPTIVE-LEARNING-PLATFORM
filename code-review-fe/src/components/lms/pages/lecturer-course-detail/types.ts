import type { Assignment } from "@/data/lms/mockData"
import type { CourseMaterial, StudentPerformanceRecord } from "@/data/lms/extendedMockData"
import type { EditableTestCase } from "@/components/lms/TestCaseManager"

export type TopicAssignment = Assignment

export type TopicBundle = {
  id: string
  courseId: string
  order: number
  title: string
  summary: string
  materials: CourseMaterial[]
  assignments: TopicAssignment[]
}

export type AssignmentDraft = {
  id: string
  topicId: string
  title: string
  description: string
  difficulty: "Easy" | "Medium" | "Hard"
  score: string
  timeLimit: string
  openAt: string
  deadline: string
  attemptsAllowed: string
  constraints: string
  examples: string
  topics: string
  starterCode: {
    python: string
    javascript: string
    java: string
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
