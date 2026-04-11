import { createSlice, type PayloadAction } from "@reduxjs/toolkit"

import {
  courseMaterials,
  courseTopics,
  initialProblemBank,
  initialSubmissionHistory,
  type CourseMaterial,
  type CourseTopic,
  type ProblemBankEntry,
  type SubmissionRecord,
} from "@/data/lms/extendedMockData"

type NewMaterialInput = Omit<CourseMaterial, "id">
type SaveProblemInput = Omit<ProblemBankEntry, "id">
type SaveProblemPatch = Partial<Omit<ProblemBankEntry, "id">>
type NewTopicInput = Pick<CourseTopic, "courseId" | "title" | "summary">
type UpdateTopicInput = Partial<Pick<CourseTopic, "title" | "summary" | "order">>
type UpdateMaterialInput = Partial<
  Pick<CourseMaterial, "title" | "type" | "resourceUrl" | "fileSize" | "previewLabel">
>

export type LmsSliceState = {
  problemBank: ProblemBankEntry[]
  topics: CourseTopic[]
  materials: CourseMaterial[]
  submissions: SubmissionRecord[]
  hasHydrated: boolean
}

const initialState: LmsSliceState = {
  problemBank: initialProblemBank,
  topics: courseTopics,
  materials: courseMaterials,
  submissions: initialSubmissionHistory,
  hasHydrated: false,
}

const createId = (prefix: string) =>
  `${prefix}-${Math.random().toString(36).slice(2, 9)}-${Date.now().toString(36)}`

const lmsSlice = createSlice({
  name: "lms",
  initialState,
  reducers: {
    hydrateLmsState: (state, action: PayloadAction<Partial<LmsSliceState> | null>) => {
      if (action.payload) {
        state.problemBank = action.payload.problemBank ?? state.problemBank
        state.topics = action.payload.topics ?? state.topics
        state.materials = action.payload.materials ?? state.materials
        state.submissions = action.payload.submissions ?? state.submissions
      }
      state.hasHydrated = true
    },
    addSubmission: (state, action: PayloadAction<SubmissionRecord>) => {
      state.submissions.unshift(action.payload)
    },
    addTopic: (state, action: PayloadAction<NewTopicInput>) => {
      const courseTopicsForCourse = state.topics.filter(
        (item) => item.courseId === action.payload.courseId
      )

      state.topics.push({
        id: createId("topic"),
        courseId: action.payload.courseId,
        order: courseTopicsForCourse.length + 1,
        title: action.payload.title,
        summary: action.payload.summary,
        materialIds: [],
        assignmentIds: [],
      })
    },
    updateTopic: (
      state,
      action: PayloadAction<{ id: string; patch: UpdateTopicInput }>
    ) => {
      state.topics = state.topics.map((topic) =>
        topic.id === action.payload.id ? { ...topic, ...action.payload.patch } : topic
      )
    },
    deleteTopic: (state, action: PayloadAction<string>) => {
      const targetTopic = state.topics.find((topic) => topic.id === action.payload)
      const nextTopics = state.topics.filter((topic) => topic.id !== action.payload)

      state.topics = nextTopics.map((topic) => {
        if (topic.courseId !== targetTopic?.courseId) {
          return topic
        }

        const courseScopedOrder =
          nextTopics
            .filter((item) => item.courseId === topic.courseId)
            .sort((left, right) => left.order - right.order)
            .findIndex((item) => item.id === topic.id) + 1

        return { ...topic, order: courseScopedOrder }
      })
      state.materials = state.materials.filter((material) => material.topicId !== action.payload)
    },
    addMaterial: (state, action: PayloadAction<NewMaterialInput>) => {
      state.materials.unshift({ ...action.payload, id: createId("material") })
    },
    updateMaterial: (
      state,
      action: PayloadAction<{ id: string; patch: UpdateMaterialInput }>
    ) => {
      state.materials = state.materials.map((material) =>
        material.id === action.payload.id
          ? { ...material, ...action.payload.patch }
          : material
      )
    },
    deleteMaterial: (state, action: PayloadAction<string>) => {
      state.materials = state.materials.filter((material) => material.id !== action.payload)
    },
    saveProblem: (
      state,
      action: PayloadAction<{ payload: SaveProblemInput; id?: string }>
    ) => {
      if (action.payload.id) {
        state.problemBank = state.problemBank.map((item) =>
          item.id === action.payload.id ? { ...item, ...action.payload.payload } : item
        )
        return
      }

      state.problemBank.unshift({
        ...action.payload.payload,
        id: createId("problem"),
      })
    },
    updateProblem: (
      state,
      action: PayloadAction<{ id: string; patch: SaveProblemPatch }>
    ) => {
      state.problemBank = state.problemBank.map((item) =>
        item.id === action.payload.id ? { ...item, ...action.payload.patch } : item
      )
    },
    attachProblemToTopic: (
      state,
      action: PayloadAction<{ assignmentId: string; topicId: string }>
    ) => {
      state.topics = state.topics.map((topic) =>
        topic.id === action.payload.topicId &&
        !topic.assignmentIds.includes(action.payload.assignmentId)
          ? { ...topic, assignmentIds: [...topic.assignmentIds, action.payload.assignmentId] }
          : topic
      )
    },
    setHasHydrated: (state, action: PayloadAction<boolean>) => {
      state.hasHydrated = action.payload
    },
  },
})

export const lmsReducer = lmsSlice.reducer
export const lmsActions = lmsSlice.actions
