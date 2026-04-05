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

type CreateTopicRequest = Pick<CourseTopic, "courseId" | "title" | "summary">
type UpdateTopicRequest = {
  id: string
  patch: Partial<Pick<CourseTopic, "title" | "summary" | "order">>
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
}
type CreatedClass = {
  id: string
  name: string
  description: string
  instructorId: string
}
export type LecturerClassSummary = {
  id: string
  name: string
  instructorName: string
  enrolledStudentsCount: number
  status: "PLANNED" | "IN_PROGRESS" | "COMPLETED" | string
}
export type LecturerClassDetail = {
  name: string
  instructorName: string
  enrolledStudentsCount: number
  createdAt: string
  status: "PLANNED" | "IN_PROGRESS" | "COMPLETED" | string
  schedule: string | null
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
    createClass: builder.mutation<CreatedClass, CreateClassRequest>({
      query: (body) => ({
        url: "/classes",
        method: "POST",
        body,
      }),
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
    createTopic: builder.mutation<CourseTopic, CreateTopicRequest>({
      query: (body) => ({
        url: "/topics",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Topic", "Course"],
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
  useCreateClassMutation,
  useAddStudentToClassMutation,
  useGetCoursesQuery,
  useGetCourseTopicsQuery,
  useGetCourseMaterialsQuery,
  useGetAssignmentsQuery,
  useGetProblemBankQuery,
  useGetSubmissionsQuery,
  useCreateTopicMutation,
  useUpdateTopicMutation,
  useDeleteTopicMutation,
  useCreateMaterialMutation,
  useUpdateMaterialMutation,
  useDeleteMaterialMutation,
  useSaveProblemMutation,
  useCreateSubmissionMutation,
} = lmsApi
