"use client"

import { useCallback, useState } from "react"

export function useKeepAliveTabs<T extends string>(defaultTab: T) {
  const [activeTab, setActiveTab] = useState<T>(defaultTab)
  const [mountedTabs, setMountedTabs] = useState<Record<string, true>>({
    [defaultTab]: true,
  })

  const handleTabChange = useCallback((nextTab: T) => {
    setActiveTab(nextTab)
    setMountedTabs((current) => {
      if (current[nextTab]) {
        return current
      }

      return {
        ...current,
        [nextTab]: true,
      }
    })
  }, [])

  const hasMounted = useCallback(
    (tab: T) => Boolean(mountedTabs[tab]),
    [mountedTabs]
  )

  return {
    activeTab,
    handleTabChange,
    hasMounted,
  }
}
