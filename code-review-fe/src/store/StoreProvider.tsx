"use client"

import { useEffect, useRef } from "react"
import { Provider } from "react-redux"

import { getCurrentUser } from "@/lib/auth"
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

    let cancelled = false

    store.dispatch(authActions.hydrateAuthState(loadPersistedAuthState()))
    store.dispatch(lmsActions.hydrateLmsState(loadPersistedLmsState()))

    const unsubscribe = store.subscribe(() => {
      const state = store.getState()
      persistAuthState(state.auth)
      persistLmsState(state.lms)
    })

    void (async () => {
      try {
        const session = await getCurrentUser()

        if (cancelled) {
          return
        }

        if (session) {
          store.dispatch(authActions.setSession(session))
        } else {
          store.dispatch(authActions.logout())
        }
      } catch {
        if (!cancelled) {
          store.dispatch(authActions.logout())
        }
      } finally {
        if (!cancelled) {
          store.dispatch(authActions.setHasHydrated(true))
        }
      }
    })()

    initialized.current = true

    return () => {
      cancelled = true
      unsubscribe()
    }
  }, [])

  return <Provider store={store}>{children}</Provider>
}
