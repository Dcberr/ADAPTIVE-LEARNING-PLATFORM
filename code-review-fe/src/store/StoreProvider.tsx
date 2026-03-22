"use client"

import { useEffect, useRef } from "react"
import { Provider } from "react-redux"

import {
  loadPersistedAuthState,
  loadPersistedLmsState,
  persistAuthState,
  persistLmsState,
} from "@/store/redux/persistence"
import { authActions } from "@/store/redux/slices/authSlice"
import { lmsActions } from "@/store/redux/slices/lmsSlice"
import { store } from "@/store/redux/store"

export default function StoreProvider({ children }: { children: React.ReactNode }) {
  const initialized = useRef(false)

  useEffect(() => {
    if (initialized.current) {
      return
    }

    store.dispatch(authActions.hydrateAuthState(loadPersistedAuthState()))
    store.dispatch(lmsActions.hydrateLmsState(loadPersistedLmsState()))

    const unsubscribe = store.subscribe(() => {
      const state = store.getState()
      persistAuthState(state.auth)
      persistLmsState(state.lms)
    })

    initialized.current = true

    return unsubscribe
  }, [])

  return <Provider store={store}>{children}</Provider>
}
