import type { Assignment, Course } from "@/data/lms/mockData"
import type {
  CourseMaterial,
  CourseTopic,
  ProblemBankEntry,
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
export type PaginatedResponse<T> = {
  content: T[]
  page: number
  size: number
  totalElements: number
  totalPages: number
}
export type ProblemBankApiProblemResponse = {
  id: string
  externalId: string
  title: string
  difficulty: string
  tags?: string[] | null
}
export type ProblemBankPageQuery = {
  page?: number
  size?: number
}
export type ProblemBankPageResult = PaginatedResponse<ProblemBankEntry>
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
type UpdateTopicRequest = {
  classId: string
  topicId: string
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
  classId: string
  topicId: string
  title: string
  description: string
  file: File
}
type UpdateDocumentRequest = {
  classId: string
  topicId: string
  documentId: string
  title?: string
  description?: string
  file?: File | null
}
type DeleteDocumentRequest = {
  classId: string
  documentId: string
}
type CreateAssignmentRequest = {
  classId: string
  topicId: string
  title: string
  startTime: string
  deadline: string
  timeLimit: number
  maxScore: number
  maxSubmission: number
  difficulty: "EASY" | "MEDIUM" | "HARD"
  tags: string[]
  problem: {
    description: string
    problemConstraint: string
    starterCodes: Record<string, string>
    testcases: Array<{
      input: string
      expectedOutput: string
      explanation: string
      hidden: boolean
    }>
  }
}
type UpdateAssignmentRequest = {
  classId: string
  assignmentId: string
  topicId?: string
  title?: string
  status?: string
  startTime?: string
  deadline?: string
  timeLimit?: number
  maxScore?: number
  maxSubmission?: number
  difficulty?: "EASY" | "MEDIUM" | "HARD"
  tags?: string[]
}
type DeleteAssignmentRequest = {
  classId: string
  assignmentId: string
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
type UpdateClassRequest = {
  classId: string
  name?: string
  description?: string
  image?: File | null
  schedule?: string
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
export type ClassStudent = {
  id: string
  email: string
  name: string
  userCode: string
  picture: string | null
  role: string
}
type AddStudentToClassRequest = {
  classId: string
  userCode: string
}
type RemoveStudentFromClassRequest = {
  classId: string
  userCode: string
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
  startedAt: string | null
  submittedAt: string
  score: string
  studentName: string
  language?: string
  runtime?: number | null
}
export type SubmissionDetailTestcaseResponse = {
  testcaseId: string
  index: number
  input: string
  expectedOutput: string
  output: string
  error: string
  status: string
  runtime: number
}
export type SubmissionDetailResponse = {
  code: string
  language: string
  testcaseResults: SubmissionDetailTestcaseResponse[]
}
export type AssignmentProblemResponse = {
  id: string
  description: string
  problemConstraint: string
  functionSkeletons: Record<string, string>
}
export type ProblemDetailResponse = {
  id: string
  externalId: string
  title: string
  description: string
  difficulty: string
  problemConstraint: string | null
  type: string
  functionSkeletons: Record<string, string>
  testcases: AssignmentTestcaseResponse[]
  similarQuestionIds: string[]
  tags: string[]
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
export type CodeReviewRequest = {
  problemId: string
  code: string
  language: string
}
export type CodeReviewLineRangeResponse = {
  start: number
  end: number
}
export type CodeReviewColumnRangeResponse = {
  start: number
  end: number
}
export type CodeReviewLinkResponse = {
  current_issue: string
  current_code_snippet: string
  previous_submission_indexes: number[]
  previous_code_snippet: string
  what_improved: string
  what_still_needs_work: string
  relation_summary: string
}
export type CodeReviewItemResponse = {
  line: CodeReviewLineRangeResponse
  column: CodeReviewColumnRangeResponse
  type: string
  issue: string
  code_snippet: string
  fix_suggestion: string
  review_link?: CodeReviewLinkResponse | null
}
export type CodeReviewScorecardMetricResponse = {
  score: number
  label: string
  explanation: string
}
export type CodeReviewResponse = {
  summary: string
  detail: string
  review_id: string
  review_items: CodeReviewItemResponse[]
  scorecard: Record<string, CodeReviewScorecardMetricResponse>
}
export type CreateSubmissionRequest = {
  problemId: string
  language: string
  code: string
  startedAt: string
}
type GetAssignmentSubmissionsRequest = {
  assignmentId: string
  scope: "me" | "all" | "user"
  userId?: string
}

function toClassSummaryFromCreate(
  createdClass: CreatedClass,
  request: CreateClassRequest
): LecturerClassSummary {
  return {
    id: createdClass.id,
    name: createdClass.name,
    instructorName: "Bạn",
    enrolledStudentsCount: 0,
    status: "PLANNED",
    schedule: request.schedule || null,
    imageUrl: createdClass.imageUrl ?? null,
  }
}

function updateClassTopicsTopic(
  topics: TopicDetailResponse[],
  topicId: string,
  updater: (topic: TopicDetailResponse) => TopicDetailResponse
) {
  const index = topics.findIndex((topic) => topic.id === topicId)
  if (index === -1) {
    return
  }

  topics[index] = updater(topics[index])
}

function removeAssignmentFromTopics(topics: TopicDetailResponse[], assignmentId: string) {
  topics.forEach((topic) => {
    topic.assignments = topic.assignments.filter((assignment) => assignment.id !== assignmentId)
  })
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
    getClassStudents: builder.query<ClassStudent[], string>({
      query: (classId) => `/classes/${classId}/students`,
      transformResponse: (response: ApiResponse<ClassStudent[]>) => response.data ?? [],
      providesTags: (result, _error, classId) => [
        { type: "Student" as const, id: `CLASS-${classId}` },
        ...(result?.map((student) => ({
          type: "Student" as const,
          id: `${classId}-${student.userCode}`,
        })) ?? []),
      ],
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
      GetAssignmentSubmissionsRequest
    >({
      query: ({ assignmentId, scope, userId }) => {
        if (scope === "me") {
          return `/submissions/assignment/${assignmentId}/me`
        }

        if (scope === "user" && userId) {
          return `/submissions/assignment/${assignmentId}/${encodeURIComponent(userId)}`
        }

        return `/submissions/assignment/${assignmentId}`
      },
      transformResponse: (response: ApiResponse<AssignmentSubmissionResponse[]>) =>
        response.data ?? [],
      providesTags: (_result, _error, { assignmentId }) => [
        { type: "Submission" as const, id: assignmentId },
      ],
    }),
    getSubmissionById: builder.query<SubmissionDetailResponse, string>({
      query: (submissionId) => `/submissions/${submissionId}`,
      transformResponse: (response: ApiResponse<SubmissionDetailResponse>) => response.data,
      providesTags: (_result, _error, submissionId) => [
        { type: "Submission" as const, id: submissionId },
      ],
    }),
    getAssignmentProblem: builder.query<AssignmentProblemResponse, string>({
      query: (assignmentId) => `/problems/assignment/${assignmentId}`,
      transformResponse: (response: ApiResponse<AssignmentProblemResponse>) => response.data,
      providesTags: (_result, _error, assignmentId) => [
        { type: "Assignment" as const, id: `PROBLEM-${assignmentId}` },
      ],
    }),
    getProblemById: builder.query<ProblemDetailResponse, string>({
      query: (problemId) => `/problems/${problemId}`,
      transformResponse: (response: ApiResponse<ProblemDetailResponse>) => response.data,
      providesTags: (_result, _error, problemId) => [{ type: "ProblemBank" as const, id: problemId }],
    }),
    getAssignmentTestcases: builder.query<AssignmentTestcaseResponse[], string>({
      query: (assignmentId) => `/testcases/assignment/${assignmentId}`,
      transformResponse: (response: ApiResponse<AssignmentTestcaseResponse[]>) => response.data,
      providesTags: (_result, _error, assignmentId) => [
        { type: "Assignment" as const, id: `TESTCASES-${assignmentId}` },
      ],
    }),
    getProblemSubmissions: builder.query<AssignmentSubmissionResponse[], string>({
      query: (problemId) => `/submissions/problem/${problemId}/me`,
      transformResponse: (response: ApiResponse<Array<{
        id: string
        language: string
        status: string
        runtime?: number | null
        submittedAt: string
        score: string
      }>>) =>
        (response.data ?? []).map((submission) => ({
          submissionId: submission.id,
          status: submission.status,
          startedAt: null,
          submittedAt: submission.submittedAt,
          score: submission.score,
          studentName: "",
          language: submission.language,
          runtime: submission.runtime ?? null,
        })),
      providesTags: (_result, _error, problemId) => [
        { type: "Submission" as const, id: `PROBLEM-${problemId}` },
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
    reviewCode: builder.mutation<CodeReviewResponse, CodeReviewRequest>({
      // Browser clients cannot safely send a request body with GET. This uses POST to the same
      // endpoint path and expects the backend/spec to align accordingly.
      query: (body) => ({
        url: "/reviews/code",
        method: "POST",
        body,
      }),
      transformResponse: (response: ApiResponse<CodeReviewResponse>) => response.data,
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
      async onQueryStarted(request, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getMyClasses", undefined, (draft) => {
              draft.unshift(toClassSummaryFromCreate(data, request))
            })
          )
        } catch {}
      },
    }),
    updateClass: builder.mutation<CreatedClass, UpdateClassRequest>({
      query: ({ classId, name, description, image, schedule }) => {
        const formData = new FormData()

        if (name !== undefined) {
          formData.append("name", name)
        }

        if (description !== undefined) {
          formData.append("description", description)
        }

        if (schedule !== undefined) {
          formData.append("schedule", schedule)
        }

        if (image) {
          formData.append("image", image)
        }

        return {
          url: `/classes/${classId}`,
          method: "PUT",
          body: formData,
        }
      },
      transformResponse: (response: ApiResponse<CreatedClass>) => response.data,
      async onQueryStarted({ classId, schedule }, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getMyClasses", undefined, (draft) => {
              const item = draft.find((classroom) => classroom.id === classId)
              if (!item) return
              item.name = data.name
              item.schedule = schedule ?? item.schedule ?? null
              item.imageUrl = data.imageUrl ?? item.imageUrl ?? null
            })
          )
          dispatch(
            baseApi.util.updateQueryData("getClassById", classId, (draft) => {
              draft.name = data.name
              draft.schedule = schedule ?? draft.schedule ?? null
              draft.imageUrl = data.imageUrl ?? draft.imageUrl ?? null
            })
          )
        } catch {}
      },
    }),
    deleteClass: builder.mutation<void, string>({
      query: (classId) => ({
        url: `/classes/${classId}`,
        method: "DELETE",
      }),
      transformResponse: () => undefined,
      async onQueryStarted(classId, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getMyClasses", undefined, (draft) =>
              draft.filter((classroom) => classroom.id !== classId)
            )
          )
        } catch {}
      },
    }),
    addStudentToClass: builder.mutation<void, AddStudentToClassRequest>({
      query: ({ classId, userCode }) => ({
        url: `/classes/${classId}/students/${encodeURIComponent(userCode)}`,
        method: "POST",
      }),
      transformResponse: () => undefined,
      async onQueryStarted({ classId }, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getMyClasses", undefined, (draft) => {
              const item = draft.find((classroom) => classroom.id === classId)
              if (item) {
                item.enrolledStudentsCount += 1
              }
            })
          )
          dispatch(
            baseApi.util.updateQueryData("getClassById", classId, (draft) => {
              draft.enrolledStudentsCount += 1
            })
          )
        } catch {}
      },
      invalidatesTags: (_result, _error, { classId }) => [
        { type: "Student" as const, id: `CLASS-${classId}` },
      ],
    }),
    removeStudentFromClass: builder.mutation<void, RemoveStudentFromClassRequest>({
      query: ({ classId, userCode }) => ({
        url: `/classes/${classId}/students/${encodeURIComponent(userCode)}`,
        method: "DELETE",
      }),
      transformResponse: () => undefined,
      async onQueryStarted({ classId, userCode }, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassStudents", classId, (draft) =>
              draft.filter((student) => student.userCode !== userCode)
            )
          )
          dispatch(
            baseApi.util.updateQueryData("getMyClasses", undefined, (draft) => {
              const item = draft.find((classroom) => classroom.id === classId)
              if (item) {
                item.enrolledStudentsCount = Math.max(0, item.enrolledStudentsCount - 1)
              }
            })
          )
          dispatch(
            baseApi.util.updateQueryData("getClassById", classId, (draft) => {
              draft.enrolledStudentsCount = Math.max(0, draft.enrolledStudentsCount - 1)
            })
          )
        } catch {}
      },
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
    getProblemBank: builder.query<ProblemBankPageResult, ProblemBankPageQuery | void>({
      query: (params) => ({
        url: "/problems/library",
        params: {
          page: params?.page ?? 0,
          size: params?.size ?? 20,
        },
      }),
      transformResponse: (
        response: ApiResponse<PaginatedResponse<ProblemBankApiProblemResponse>>
      ) => ({
        ...response.data,
        content: response.data.content.map((problem) => ({
          id: problem.id,
          title: problem.title,
          description: "",
          difficulty: problem.difficulty,
          topics: problem.tags ?? [],
          tags: problem.tags ?? [],
          estimatedMinutes:
            problem.difficulty === "HARD" ? 50 : problem.difficulty === "MEDIUM" ? 35 : 20,
          recommendedForCourseIds: [],
          solvedByStudentIds: [],
          source: "bank",
        })),
      }),
      providesTags: (result) => [
        { type: "ProblemBank" as const, id: "LIST" },
        ...(result?.content.map((problem) => ({ type: "ProblemBank" as const, id: problem.id })) ?? []),
      ],
    }),
    createTopic: builder.mutation<CreatedTopic, CreateTopicRequest>({
      query: (body) => ({
        url: "/topics",
        method: "POST",
        body,
      }),
      transformResponse: (response: ApiResponse<CreatedTopic>) => response.data,
      async onQueryStarted({ classId }, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
              draft.push({
                id: data.id,
                title: data.title,
                description: data.description,
                assignments: [],
                documents: [],
              })
            })
          )
        } catch {}
      },
    }),
    updateTopic: builder.mutation<
      CreatedTopic,
      UpdateTopicRequest
    >({
        query: ({ topicId, title, description }) => ({
          url: `/topics/${topicId}`,
          method: "PUT",
          body: {
            title,
            description,
          },
        }),
        transformResponse: (response: ApiResponse<CreatedTopic>) => response.data,
        async onQueryStarted({ classId, topicId }, { dispatch, queryFulfilled }) {
          try {
            const { data } = await queryFulfilled
            dispatch(
              baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
                updateClassTopicsTopic(draft, topicId, (topic) => ({
                  ...topic,
                  title: data.title,
                  description: data.description,
                }))
              })
            )
          } catch {}
        },
      }),
    deleteTopic: builder.mutation<void, { classId: string; topicId: string }>({
      query: ({ topicId }) => ({
        url: `/topics/${topicId}`,
        method: "DELETE",
      }),
      transformResponse: () => undefined,
      async onQueryStarted({ classId, topicId }, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) =>
              draft.filter((topic) => topic.id !== topicId)
            )
          )
        } catch {}
      },
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
      async onQueryStarted({ classId, topicId }, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
              updateClassTopicsTopic(draft, topicId, (topic) => ({
                ...topic,
                documents: [...topic.documents, data],
              }))
            })
          )
        } catch {}
      },
    }),
    updateDocument: builder.mutation<TopicDocumentResponse, UpdateDocumentRequest>({
      query: ({ documentId, title, description, file }) => {
        const formData = new FormData()

        if (title !== undefined) {
          formData.append("title", title)
        }

        if (description !== undefined) {
          formData.append("description", description)
        }

        if (file) {
          formData.append("file", file)
        }

        return {
          url: `/documents/${documentId}`,
          method: "PUT",
          body: formData,
        }
      },
      transformResponse: (response: ApiResponse<TopicDocumentResponse>) => response.data,
      async onQueryStarted({ classId, topicId, documentId }, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
              updateClassTopicsTopic(draft, topicId, (topic) => ({
                ...topic,
                documents: topic.documents.map((document) =>
                  document.id === documentId ? data : document
                ),
              }))
            })
          )
        } catch {}
      },
    }),
    deleteDocument: builder.mutation<void, DeleteDocumentRequest>({
      query: ({ documentId }) => ({
        url: `/documents/${documentId}`,
        method: "DELETE",
      }),
      transformResponse: () => undefined,
      async onQueryStarted({ classId, documentId }, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
              draft.forEach((topic) => {
                topic.documents = topic.documents.filter((document) => document.id !== documentId)
              })
            })
          )
        } catch {}
      },
    }),
    createAssignment: builder.mutation<TopicAssignmentResponse, CreateAssignmentRequest>({
      query: (request) => ({
        url: "/assignments",
        method: "POST",
        body: {
          topicId: request.topicId,
          title: request.title,
          startTime: request.startTime,
          deadline: request.deadline,
          timeLimit: request.timeLimit,
          maxScore: request.maxScore,
          maxSubmission: request.maxSubmission,
          difficulty: request.difficulty,
          tags: request.tags,
          problem: request.problem,
        },
      }),
      transformResponse: (response: ApiResponse<TopicAssignmentResponse>) => response.data,
      async onQueryStarted({ classId, topicId }, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
              updateClassTopicsTopic(draft, topicId, (topic) => ({
                ...topic,
                assignments: [...topic.assignments, data],
              }))
            })
          )
        } catch {}
      },
    }),
    updateAssignment: builder.mutation<TopicAssignmentResponse, UpdateAssignmentRequest>({
      query: (request) => ({
        url: `/assignments/${request.assignmentId}`,
        method: "PUT",
        body: {
          topicId: request.topicId,
          title: request.title,
          status: request.status,
          startTime: request.startTime,
          deadline: request.deadline,
          timeLimit: request.timeLimit,
          maxScore: request.maxScore,
          maxSubmission: request.maxSubmission,
          difficulty: request.difficulty,
          tags: request.tags,
        },
      }),
      transformResponse: (response: ApiResponse<TopicAssignmentResponse>) => response.data,
      async onQueryStarted({ classId, assignmentId, topicId }, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
              const currentTopic = draft.find((topic) =>
                topic.assignments.some((assignment) => assignment.id === assignmentId)
              )
              const resolvedTopicId = topicId ?? currentTopic?.id
              removeAssignmentFromTopics(draft, assignmentId)

              if (resolvedTopicId) {
                updateClassTopicsTopic(draft, resolvedTopicId, (topic) => ({
                  ...topic,
                  assignments: [...topic.assignments, data],
                }))
              }
            })
          )
        } catch {}
      },
    }),
    deleteAssignment: builder.mutation<void, DeleteAssignmentRequest>({
      query: ({ assignmentId }) => ({
        url: `/assignments/${assignmentId}`,
        method: "DELETE",
      }),
      transformResponse: () => undefined,
      async onQueryStarted({ classId, assignmentId }, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled
          dispatch(
            baseApi.util.updateQueryData("getClassTopics", classId, (draft) => {
              removeAssignmentFromTopics(draft, assignmentId)
            })
          )
        } catch {}
      },
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
      invalidatesTags: (result) => [
        { type: "ProblemBank" as const, id: "LIST" },
        ...(result ? [{ type: "ProblemBank" as const, id: result.id }] : []),
      ],
    }),
    createSubmission: builder.mutation<AssignmentSubmissionResponse, CreateSubmissionRequest>({
      query: (body) => ({
        url: "/submissions",
        method: "POST",
        body,
      }),
      transformResponse: (response: ApiResponse<AssignmentSubmissionResponse>) => response.data,
      invalidatesTags: ["Submission", "Assignment", "Student"],
    }),
  }),
})

export const {
  useGetMyClassesQuery,
  useGetClassByIdQuery,
  useGetClassStudentsQuery,
  useGetClassTopicsQuery,
  useGetAssignmentContextQuery,
  useGetAssignmentSubmissionsQuery,
  useGetSubmissionByIdQuery,
  useGetAssignmentProblemQuery,
  useGetProblemByIdQuery,
  useGetAssignmentTestcasesQuery,
  useGetProblemSubmissionsQuery,
  useJudgeExecutionMutation,
  useReviewCodeMutation,
  useCreateClassMutation,
  useUpdateClassMutation,
  useDeleteClassMutation,
  useAddStudentToClassMutation,
  useRemoveStudentFromClassMutation,
  useGetCoursesQuery,
  useGetCourseTopicsQuery,
  useGetCourseMaterialsQuery,
  useGetAssignmentsQuery,
  useGetProblemBankQuery,
  useCreateTopicMutation,
  useUpdateTopicMutation,
  useDeleteTopicMutation,
  useCreateDocumentMutation,
  useUpdateDocumentMutation,
  useDeleteDocumentMutation,
  useCreateAssignmentMutation,
  useUpdateAssignmentMutation,
  useDeleteAssignmentMutation,
  useCreateMaterialMutation,
  useUpdateMaterialMutation,
  useDeleteMaterialMutation,
  useSaveProblemMutation,
  useCreateSubmissionMutation,
} = lmsApi
