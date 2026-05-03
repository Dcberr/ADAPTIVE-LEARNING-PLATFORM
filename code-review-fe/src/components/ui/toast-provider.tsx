"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"
import { AlertCircle, CheckCircle2, Info, X } from "lucide-react"

import { cn } from "@/lib/utils"

type ToastTone = "success" | "error" | "info"

type ToastInput = {
  title?: string
  description: string
  tone?: ToastTone
  duration?: number
}

type ToastRecord = ToastInput & {
  id: string
}

type ToastContextValue = {
  toast: (input: ToastInput) => void
}

const MAX_TOASTS = 3

const ToastContext = createContext<ToastContextValue | null>(null)

const toneStyles: Record<
  ToastTone,
  {
    icon: typeof CheckCircle2
    className: string
  }
> = {
  success: {
    icon: CheckCircle2,
    className: "border-emerald-600 bg-white text-emerald-700 shadow-emerald-900/10",
  },
  error: {
    icon: AlertCircle,
    className: "border-rose-600 bg-white text-rose-700 shadow-rose-900/10",
  },
  info: {
    icon: Info,
    className: "border-sky-600 bg-white text-sky-700 shadow-sky-900/10",
  },
}

function ToastViewport({
  toasts,
  onDismiss,
}: {
  toasts: ToastRecord[]
  onDismiss: (id: string) => void
}) {
  return (
    <div className="pointer-events-none fixed left-1/2 top-4 z-[120] flex w-[min(380px,calc(100vw-2rem))] -translate-x-1/2 flex-col gap-3">
      {toasts.map((toast) => {
        const tone = toast.tone ?? "info"
        const Icon = toneStyles[tone].icon

        return (
          <div
            key={toast.id}
            className={cn(
              "pointer-events-auto rounded-2xl border px-4 py-3 shadow-lg backdrop-blur-sm",
              "animate-in slide-in-from-top-2 fade-in-0",
              toneStyles[tone].className
            )}
            role="status"
            aria-live="polite"
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 rounded-full bg-current/10 p-1.5">
                <Icon className="size-4" />
              </div>
              <div className="min-w-0 flex-1">
                {toast.title ? <p className="text-sm font-semibold">{toast.title}</p> : null}
                <p className="text-sm leading-6 text-slate-700">{toast.description}</p>
              </div>
              <button
                type="button"
                className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                onClick={() => onDismiss(toast.id)}
                aria-label="Dismiss notification"
              >
                <X className="size-4" />
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastRecord[]>([])

  const dismissToast = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const toast = useCallback(
    ({ duration = 3200, tone = "info", ...input }: ToastInput) => {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
      setToasts((current) => [
        ...current.slice(-(MAX_TOASTS - 1)),
        { id, tone, duration, ...input },
      ])
    },
    []
  )

  useEffect(() => {
    if (toasts.length === 0) {
      return
    }

    const timers = toasts.map((item) =>
      window.setTimeout(() => {
        dismissToast(item.id)
      }, item.duration ?? 3200)
    )

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer))
    }
  }, [dismissToast, toasts])

  const value = useMemo(() => ({ toast }), [toast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)

  if (!context) {
    throw new Error("useToast must be used within ToastProvider")
  }

  return context
}
