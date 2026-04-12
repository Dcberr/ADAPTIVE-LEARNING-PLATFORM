"use client"

import { useMemo } from "react"

import { codeReviewActions } from "@/store/redux/slices/codeReviewSlice"
import { useAppDispatch, useAppSelector } from "@/store/redux/hooks"
import { store, type RootState } from "@/store/redux/store"

type ReviewItem = {
  line: number
  message: string
  suggestion?: string
  type: "error" | "warning"
}

type CodeStoreShape = {
  code: string
  setCode: (val: string) => void
  review: {
    errors: ReviewItem[]
    warnings: ReviewItem[]
    improvements: string[]
    understanding: string
  } | null
  setReview: (val: CodeStoreShape["review"]) => void
}

function buildCodeStoreApi(state: RootState, dispatch = store.dispatch): CodeStoreShape {
  return {
    code: state.codeReview.code,
    review: state.codeReview.review,
    setCode: (val) => dispatch(codeReviewActions.setCode(val)),
    setReview: (val) => dispatch(codeReviewActions.setReview(val)),
  }
}

export function useCodeStore<T = CodeStoreShape>(
  selector: (state: CodeStoreShape) => T = ((state: CodeStoreShape) => state as T)
) {
  const dispatch = useAppDispatch()
  const codeState = useAppSelector((state) => state.codeReview)
  const api = useMemo(
    () => buildCodeStoreApi({ ...store.getState(), codeReview: codeState }, dispatch),
    [codeState, dispatch]
  )

  return selector(api)
}

useCodeStore.getState = () => buildCodeStoreApi(store.getState())
