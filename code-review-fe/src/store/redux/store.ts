import { configureStore } from "@reduxjs/toolkit"
import { setupListeners } from "@reduxjs/toolkit/query"

import { baseApi } from "@/store/redux/api/baseApi"
import { authReducer } from "@/store/redux/slices/authSlice"
import { codeReviewReducer } from "@/store/redux/slices/codeReviewSlice"
import { lmsReducer } from "@/store/redux/slices/lmsSlice"

export const store = configureStore({
  reducer: {
    [baseApi.reducerPath]: baseApi.reducer,
    auth: authReducer,
    lms: lmsReducer,
    codeReview: codeReviewReducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(baseApi.middleware),
})

setupListeners(store.dispatch)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
