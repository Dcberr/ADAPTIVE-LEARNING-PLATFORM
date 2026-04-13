import type { Assignment, Course } from "@/data/lms/mockData"
import type {
  CourseMaterial,
  CourseTopic,
  ProblemBankEntry,
  SubmissionRecord,
} from "@/data/lms/extendedMockData"
import { baseApi } from "@/store/redux/api/baseApi"

type ApiResponse<T> = {
  success: boolean
  message: string
  data: T
  timestamp: string
}

type TopicOverviewResponse = {
  ids: string[]
}
type TopicBaseDetailResponse = {
  id: string
  title: string
  description: string
}
export type TopicAssignmentResponse = {
  id: string
  title: string
  deadline: string
  difficulty: "EASY" | "MEDIUM" | "HARD" | string
  startTime?: string | null
  timeLimit?: number | null
  maxScore?: number | null
  maxSubmission?: number | null
  tags?: string[] | null
  status: string
}
export type TopicDocumentResponse = {
  id: string
  title: string
  description: string
  fileUrl: string
  type: string
}
export type TopicDetailResponse = {
  id: string
  title: string
  description: string
  assignments: TopicAssignmentResponse[]
  documents: TopicDocumentResponse[]
}
type CreateTopicRequest = {
  classId: string
  title: string
  description: string
}
type CreatedTopic = {
  id: string
  classId: string
  title: string
  description: string
}
type CreateDocumentRequest = {
  topicId: string
  title: string
  description: string
  file: File
}
type CreateAssignmentRequest = {
  topicId: string
  title: string
  startTime: string
  deadline: string
  timeLimit: number
  maxScore: number
  maxSubmission: number
  difficulty: "EASY" | "MEDIUM" | "HARD"
  tags: string[]
  description: string
  problemConstraint: string
  functionSkeletons: Record<string, string>
  testcases: Array<{
    input: string
    expectedOutput: string
    explanation: string
    hidden: boolean
  }>
}
type UpdateTopicRequest = {
  id: string
  patch: Partial<{
    title: string
    summary: string
    order: number
  }>
}
type CreateMaterialRequest = Omit<CourseMaterial, "id">
type UpdateMaterialRequest = {
  id: string
  patch: Partial<
    Pick<CourseMaterial, "title" | "type" | "resourceUrl" | "fileSize" | "previewLabel">
  >
}
type SaveProblemRequest = {
  id?: string
  payload: Omit<ProblemBankEntry, "id">
}
type CreateClassRequest = {
  name: string
  description: string
  image: File | null
  schedule: string
}
type CreatedClass = {
  id: string
  name: string
  description: string
  instructorId: string
  imageUrl: string | null
}
export type LecturerClassSummary = {
  id: string
  name: string
  instructorName: string
  enrolledStudentsCount: number
  status: "PLANNED" | "IN_PROGRESS" | "COMPLETED" | string
  schedule?: string | null
  imageUrl?: string | null
}
export type LecturerClassDetail = {
  name: string
  instructorName: string
  enrolledStudentsCount: number
  createdAt: string
  status: "PLANNED" | "IN_PROGRESS" | "COMPLETED" | string
  schedule: string | null
  imageUrl?: string | null
}
type AddStudentToClassRequest = {
  classId: string
  studentId: string
}
export type AssignmentContext = TopicAssignmentResponse & {
  topicId: string
  topicTitle: string
  classId: string
  className: string
  instructorName: string
  imageUrl?: string | null
}
export type AssignmentSubmissionResponse = {
  submissionId: string
  status: string
  startedAt: string
  submittedAt: string
  score: string
  studentName: string
}
export type AssignmentProblemResponse = {
  id: string
  description: string
  problemConstraint: string
  functionSkeletons: Record<string, string>
}
export type AssignmentTestcaseResponse = {
  id: string
  problemId: string
  input: string
  expectedOutput: string
  explanation: string
  hidden: boolean
}
export type JudgeExecutionRequest = {
  problemId: string
  language: string
  code: string
}
export type JudgeExecutionTestcaseResponse = {
  testcaseId: string | null
  index: number
  input: string
  expectedOutput: string
  output: string
  error: string
  status: string
  runtime: number
}
export type JudgeExecutionResponse = {
  status: string
  testcases: JudgeExecutionTestcaseResponse[]
  passedTestcases: number
  totalTestcases: number
  runtime: number
}

export const lmsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getMyClasses: builder.query<LecturerClassSummary[], void>({
      query: () => "/classes/me",
      transformResponse: (response: ApiResponse<LecturerClassSummary[]>) => response.data,
      providesTags: (result) => [
        { type: "Class" as const, id: "LIST" },
        ...(result?.map((item) => ({ type: "Class" as const, id: item.id })) ?? []),
      ],
    }),
    getClassById: builder.query<LecturerClassDetail, string>({
      query: (classId) => `/classes/${classId}`,
      transformResponse: (response: ApiResponse<LecturerClassDetail>) => response.data,
      providesTags: (_result, _error, classId) => [{ type: "Class" as const, id: classId }],
    }),
    getClassTopics: builder.query<TopicDetailResponse[], string>({
      async queryFn(classId, _api, _extraOptions, fetchWithBQ) {
        const overviewResult = await fetchWithBQ(`/topics/class/${classId}`)

        if (overviewResult.error) {
          return { error: overviewResult.error }
        }

        const overviewPayload = overviewResult.data as ApiResponse<TopicOverviewResponse>
        const topicIds = overviewPayload.data.ids ?? []

        if (topicIds.length === 0) {
          return { data: [] }
        }

        const topicResults = await Promise.all(
          topicIds.map(async (topicId) => {
            const [topicResult, documentsResult, assignmentsResult] = await Promise.all([
              fetchWithBQ(`/topics/${topicId}`),
              fetchWithBQ(`/documents/topic/${topicId}`),
              fetchWithBQ(`/assignments/topic/${topicId}`),
            ])

            return {
              topicId,
              topicResult,
              documentsResult,
              assignmentsResult,
            }
          })
        )
        const failedResult = topicResults.find(
          (result) =>
            result.topicResult.error ||
            result.documentsResult.error ||
            result.assignmentsResult.error
        )

        if (failedResult?.topicResult.error) {
          return { error: failedResult.topicResult.error }
        }

        if (failedResult?.documentsResult.error) {
          return { error: failedResult.documentsResult.error }
        }

        if (failedResult?.assignmentsResult.error) {
          return { error: failedResult.assignmentsResult.error }
        }

        const topics = topicResults.map((result) => {
          const topicPayload = result.topicResult.data as ApiResponse<TopicBaseDetailResponse>
          const documentsPayload = result.documentsResult.data as ApiResponse<TopicDocumentResponse[]>
          const assignmentsPayload =
            result.assignmentsResult.data as ApiResponse<TopicAssignmentResponse[]>

          return {
            id: topicPayload.data.id,
            title: topicPayload.data.title,
            description: topicPayload.data.description,
            documents: documentsPayload.data,
            assignments: assignmentsPayload.data,
          }
        })

        return { data: topics }
      },
      providesTags: (result, _error, classId) => [
        { type: "Topic" as const, id: `CLASS-${classId}` },
        ...(result?.map((topic) => ({ type: "Topic" as const, id: topic.id })) ?? []),
      ],
    }),
    getAssignmentContext: builder.query<AssignmentContext, string>({
      async queryFn(assignmentId, _api, _extraOptions, fetchWithBQ) {
        const classesResult = await fetchWithBQ("/classes/me")

        if (classesResult.error) {
          return { error: classesResult.error }
        }

        const classesPayload = classesResult.data as ApiResponse<LecturerClassSummary[]>
        const classes = classesPayload.data ?? []

        for (const classroom of classes) {
          const topicsResult = await fetchWithBQ(`/topics/class/${classroom.id}`)

          if (topicsResult.error) {
            return { error: topicsResult.error }
          }

          const topicsPayload = topicsResult.data as ApiResponse<TopicOverviewResponse>
          const topicIds = topicsPayload.data.ids ?? []

          for (const topicId of topicIds) {
            const [topicResult, assignmentsResult] = await Promise.all([
              fetchWithBQ(`/topics/${topicId}`),
              fetchWithBQ(`/assignments/topic/${topicId}`),
            ])

            if (topicResult.error) {
              return { error: topicResult.error }
            }

            if (assignmentsResult.error) {
              return { error: assignmentsResult.error }
            }

            const topicPayload = topicResult.data as ApiResponse<TopicBaseDetailResponse>
            const assignmentsPayload =
              assignmentsResult.data as ApiResponse<TopicAssignmentResponse[]>
            const assignment = (assignmentsPayload.data ?? []).find((item) => item.id === assignmentId)

            if (assignment) {
              return {
                data: {
                  ...assignment,
                  topicId,
                  topicTitle: topicPayload.data.title,
                  classId: classroom.id,
                  className: classroom.name,
                  instructorName: classroom.instructorName,
                  imageUrl: classroom.imageUrl,
                },
              }
            }
          }
        }

        return {
          error: {
            status: 404,
            data: "Assignment not found",
          },
        }
      },
      providesTags: (_result, _error, assignmentId) => [
        { type: "Assignment" as const, id: assignmentId },
      ],
    }),
    getAssignmentSubmissions: builder.query<
      AssignmentSubmissionResponse[],
      { assignmentId: string; scope: "me" | "all" }
    >({
      query: ({ assignmentId, scope }) =>
        scope === "me"
          ? `/submissions/assignment/${assignmentId}/me`
          : `/submissions/assignment/${assignmentId}`,
      transformResponse: (response: ApiResponse<AssignmentSubmissionResponse[]>) => response.data,
      providesTags: (_result, _error, { assignmentId }) => [
        { type: "Submission" as const, id: assignmentId },
      ],
    }),
    getAssignmentProblem: builder.query<AssignmentProblemResponse, string>({
      query: (assignmentId) => `/problems/assignment/${assignmentId}`,
      transformResponse: (response: ApiResponse<AssignmentProblemResponse>) => response.data,
      providesTags: (_result, _error, assignmentId) => [
        { type: "Assignment" as const, id: `PROBLEM-${assignmentId}` },
      ],
    }),
    getAssignmentTestcases: builder.query<AssignmentTestcaseResponse[], string>({
      query: (assignmentId) => `/testcases/assignment/${assignmentId}`,
      transformResponse: (response: ApiResponse<AssignmentTestcaseResponse[]>) => response.data,
      providesTags: (_result, _error, assignmentId) => [
        { type: "Assignment" as const, id: `TESTCASES-${assignmentId}` },
      ],
    }),
    judgeExecution: builder.mutation<JudgeExecutionResponse, JudgeExecutionRequest>({
      query: (body) => ({
        url: "/execution/judge",
        method: "POST",
        body,
      }),
      transformResponse: (response: ApiResponse<JudgeExecutionResponse>) => response.data,
    }),
    createClass: builder.mutation<CreatedClass, CreateClassRequest>({
      query: ({ name, description, image, schedule }) => {
        const formData = new FormData()
        formData.append("name", name)
        formData.append("description", description)
        formData.append("schedule", schedule)

        if (image) {
          formData.append("image", image)
        }

        return {
          url: "/classes",
          method: "POST",
          body: formData,
        }
      },
      transformResponse: (response: ApiResponse<CreatedClass>) => response.data,
      invalidatesTags: [{ type: "Class" as const, id: "LIST" }],
    }),
    addStudentToClass: builder.mutation<null, AddStudentToClassRequest>({
      query: ({ classId, studentId }) => ({
        url: `/classes/${classId}/students`,
        method: "POST",
        body: { studentId },
      }),
      transformResponse: (response: ApiResponse<null>) => response.data,
      invalidatesTags: (_result, _error, { classId }) => [
        { type: "Class" as const, id: "LIST" },
        { type: "Class" as const, id: classId },
      ],
    }),
    getCourses: builder.query<Course[], void>({
      query: () => "/courses",
      providesTags: ["Course"],
    }),
    getCourseTopics: builder.query<CourseTopic[], string>({
      query: (courseId) => `/courses/${courseId}/topics`,
      providesTags: (_result, _error, courseId) => [
        "Topic",
        { type: "Course" as const, id: courseId },
      ],
    }),
    getCourseMaterials: builder.query<CourseMaterial[], string>({
      query: (courseId) => `/courses/${courseId}/materials`,
      providesTags: (_result, _error, courseId) => [
        "Material",
        { type: "Course" as const, id: courseId },
      ],
    }),
    getAssignments: builder.query<Assignment[], string | void>({
      query: (courseId) => (courseId ? `/courses/${courseId}/assignments` : "/assignments"),
      providesTags: ["Assignment"],
    }),
    getProblemBank: builder.query<ProblemBankEntry[], void>({
      query: () => "/problem-bank",
      providesTags: ["ProblemBank"],
    }),
    getSubmissions: builder.query<SubmissionRecord[], string | void>({
      query: (assignmentId) =>
        assignmentId ? `/assignments/${assignmentId}/submissions` : "/submissions",
      providesTags: ["Submission"],
    }),
    createTopic: builder.mutation<CreatedTopic, CreateTopicRequest>({
      query: (body) => ({
        url: "/topics",
        method: "POST",
        body,
      }),
      transformResponse: (response: ApiResponse<CreatedTopic>) => response.data,
      invalidatesTags: (_result, _error, { classId }) => [
        { type: "Topic" as const, id: `CLASS-${classId}` },
        { type: "Class" as const, id: classId },
      ],
    }),
    createDocument: builder.mutation<TopicDocumentResponse, CreateDocumentRequest>({
      query: ({ topicId, title, description, file }) => {
        const formData = new FormData()
        formData.append("topicId", topicId)
        formData.append("title", title)
        formData.append("description", description)
        formData.append("file", file)

        return {
          url: "/documents",
          method: "POST",
          body: formData,
        }
      },
      transformResponse: (response: ApiResponse<TopicDocumentResponse>) => response.data,
      invalidatesTags: (_result, _error, { topicId }) => [
        { type: "Topic" as const, id: topicId },
        "Topic",
        "Material",
      ],
    }),
    createAssignment: builder.mutation<TopicAssignmentResponse, CreateAssignmentRequest>({
      query: ({
        topicId,
        title,
        startTime,
        deadline,
        timeLimit,
        maxScore,
        maxSubmission,
        difficulty,
        tags,
        description,
        problemConstraint,
        functionSkeletons,
        testcases,
      }) => ({
        url: "/assignments",
        method: "POST",
        body: {
          topicId,
          title,
          startTime,
          deadline,
          timeLimit,
          maxScore,
          maxSubmission,
          difficulty,
          tags,
          problem: {
            description,
            problemConstraint,
            functionSkeletons,
            testcases,
          },
        },
      }),
      transformResponse: (response: ApiResponse<TopicAssignmentResponse>) => response.data,
      invalidatesTags: (_result, _error, { topicId }) => [
        { type: "Topic" as const, id: topicId },
        "Assignment",
        "Topic",
      ],
    }),
    updateTopic: builder.mutation<CourseTopic, UpdateTopicRequest>({
      query: ({ id, patch }) => ({
        url: `/topics/${id}`,
        method: "PATCH",
        body: patch,
      }),
      invalidatesTags: ["Topic", "Course"],
    }),
    deleteTopic: builder.mutation<{ success: boolean; id: string }, string>({
      query: (id) => ({
        url: `/topics/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Topic", "Course", "Material"],
    }),
    createMaterial: builder.mutation<CourseMaterial, CreateMaterialRequest>({
      query: (body) => ({
        url: "/materials",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Material", "Course"],
    }),
    updateMaterial: builder.mutation<CourseMaterial, UpdateMaterialRequest>({
      query: ({ id, patch }) => ({
        url: `/materials/${id}`,
        method: "PATCH",
        body: patch,
      }),
      invalidatesTags: ["Material", "Course"],
    }),
    deleteMaterial: builder.mutation<{ success: boolean; id: string }, string>({
      query: (id) => ({
        url: `/materials/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Material", "Course"],
    }),
    saveProblem: builder.mutation<ProblemBankEntry, SaveProblemRequest>({
      query: ({ id, payload }) => ({
        url: id ? `/problem-bank/${id}` : "/problem-bank",
        method: id ? "PUT" : "POST",
        body: payload,
      }),
      invalidatesTags: ["ProblemBank", "Assignment"],
    }),
    createSubmission: builder.mutation<SubmissionRecord, SubmissionRecord>({
      query: (body) => ({
        url: "/submissions",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Submission", "Assignment", "Student"],
    }),
  }),
})

export const {
  useGetMyClassesQuery,
  useGetClassByIdQuery,
  useGetClassTopicsQuery,
  useGetAssignmentContextQuery,
  useGetAssignmentSubmissionsQuery,
  useGetAssignmentProblemQuery,
  useGetAssignmentTestcasesQuery,
  useJudgeExecutionMutation,
  useCreateClassMutation,
  useAddStudentToClassMutation,
  useGetCoursesQuery,
  useGetCourseTopicsQuery,
  useGetCourseMaterialsQuery,
  useGetAssignmentsQuery,
  useGetProblemBankQuery,
  useGetSubmissionsQuery,
  useCreateTopicMutation,
  useCreateDocumentMutation,
  useCreateAssignmentMutation,
  useUpdateTopicMutation,
  useDeleteTopicMutation,
  useCreateMaterialMutation,
  useUpdateMaterialMutation,
  useDeleteMaterialMutation,
  useSaveProblemMutation,
  useCreateSubmissionMutation,
} = lmsApi
