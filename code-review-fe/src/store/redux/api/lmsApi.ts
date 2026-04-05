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
  deadline: string
  difficulty: "Easy" | "Medium" | "Hard"
  description: string
  testcases: Array<{
    input: string
    expectedOutput: string
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
  image: File
  schedule: string
}
type CreatedClass = {
  id: string
  name: string
  description: string
  instructorId: string
  imageUrl: string
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
    createClass: builder.mutation<CreatedClass, CreateClassRequest>({
      query: ({ name, description, image, schedule }) => {
        const formData = new FormData()
        formData.append("name", name)
        formData.append("description", description)
        formData.append("image", image)
        formData.append("schedule", schedule)

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
      query: ({ topicId, title, deadline, difficulty, description, testcases }) => ({
        url: "/assignments",
        method: "POST",
        body: {
          topicId,
          title,
          deadline,
          difficulty: difficulty.toUpperCase(),
          problem: {
            description,
            testcases: testcases.map((testcase) => ({
              input: testcase.input,
              expectedOutput: testcase.expectedOutput,
              explanation: "",
              sample: !testcase.hidden,
            })),
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
