"use client"

import { useMemo } from "react"

import type {
  CourseMaterial,
  CourseTopic,
  ProblemBankEntry,
  SubmissionRecord,
} from "@/data/lms/extendedMockData"
import { lmsActions } from "@/store/redux/slices/lmsSlice"
import { useAppDispatch, useAppSelector } from "@/store/redux/hooks"
import { store, type RootState } from "@/store/redux/store"

type NewMaterialInput = Omit<CourseMaterial, "id">
type SaveProblemInput = Omit<ProblemBankEntry, "id">
type SaveProblemPatch = Partial<Omit<ProblemBankEntry, "id">>
type NewTopicInput = Pick<CourseTopic, "courseId" | "title" | "summary">
type UpdateTopicInput = Partial<Pick<CourseTopic, "title" | "summary" | "order">>
type UpdateMaterialInput = Partial<
  Pick<CourseMaterial, "title" | "type" | "resourceUrl" | "fileSize" | "previewLabel">
>

type LmsStoreShape = {
  problemBank: ProblemBankEntry[]
  topics: CourseTopic[]
  materials: CourseMaterial[]
  submissions: SubmissionRecord[]
  hasHydrated: boolean
  addSubmission: (submission: SubmissionRecord) => void
  addTopic: (topic: NewTopicInput) => void
  updateTopic: (id: string, patch: UpdateTopicInput) => void
  deleteTopic: (id: string) => void
  addMaterial: (material: NewMaterialInput) => void
  updateMaterial: (id: string, patch: UpdateMaterialInput) => void
  deleteMaterial: (id: string) => void
  saveProblem: (payload: SaveProblemInput, id?: string) => void
  attachProblemToTopic: (assignmentId: string, topicId: string) => void
  updateProblem: (id: string, patch: SaveProblemPatch) => void
  setHasHydrated: (value: boolean) => void
}

function buildLmsStoreApi(state: RootState, dispatch = store.dispatch): LmsStoreShape {
  return {
    problemBank: state.lms.problemBank,
    topics: state.lms.topics,
    materials: state.lms.materials,
    submissions: state.lms.submissions,
    hasHydrated: state.lms.hasHydrated,
    addSubmission: (submission) => dispatch(lmsActions.addSubmission(submission)),
    addTopic: (topic) => dispatch(lmsActions.addTopic(topic)),
    updateTopic: (id, patch) => dispatch(lmsActions.updateTopic({ id, patch })),
    deleteTopic: (id) => dispatch(lmsActions.deleteTopic(id)),
    addMaterial: (material) => dispatch(lmsActions.addMaterial(material)),
    updateMaterial: (id, patch) => dispatch(lmsActions.updateMaterial({ id, patch })),
    deleteMaterial: (id) => dispatch(lmsActions.deleteMaterial(id)),
    saveProblem: (payload, id) => dispatch(lmsActions.saveProblem({ payload, id })),
    attachProblemToTopic: (assignmentId, topicId) =>
      dispatch(lmsActions.attachProblemToTopic({ assignmentId, topicId })),
    updateProblem: (id, patch) => dispatch(lmsActions.updateProblem({ id, patch })),
    setHasHydrated: (value) => dispatch(lmsActions.setHasHydrated(value)),
  }
}

export function useLmsStore<T = LmsStoreShape>(
  selector: (state: LmsStoreShape) => T = ((state: LmsStoreShape) => state as T)
) {
  const dispatch = useAppDispatch()
  const lmsState = useAppSelector((state) => state.lms)
  const api = useMemo(
    () => buildLmsStoreApi({ ...store.getState(), lms: lmsState }, dispatch),
    [dispatch, lmsState]
  )

  return selector(api)
}

useLmsStore.getState = () => buildLmsStoreApi(store.getState())
