"use client"

import { useEffect, useRef, type FormEvent } from "react"
import { LoaderCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

type FeedbackState =
  | {
      tone: "success" | "error"
      message: string
    }
  | null

export default function CreateClassCard({
  draft,
  feedback,
  isCreating,
  onChange,
  onSubmit,
}: {
  draft: {
    name: string
    description: string
    image: File | null
    schedule: string
  }
  feedback: FeedbackState
  isCreating: boolean
  onChange: (
    patch: Partial<{ name: string; description: string; image: File | null; schedule: string }>
  ) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!draft.image && fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }, [draft.image])

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="class-name">
          Class name
        </label>
        <Input
          id="class-name"
          value={draft.name}
          onChange={(event) => onChange({ name: event.target.value })}
          placeholder="OOP K24 - Group 2"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="class-description">
          Description
        </label>
        <Textarea
          id="class-description"
          value={draft.description}
          onChange={(event) => onChange({ description: event.target.value })}
          placeholder="Describe the class scope or notes for this section."
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="class-image">
          Class image
        </label>
        <Input
          ref={fileInputRef}
          id="class-image"
          type="file"
          accept="image/*"
          onChange={(event) => onChange({ image: event.target.files?.[0] ?? null })}
        />
        <p className="text-xs text-slate-500">
          {draft.image ? `Selected: ${draft.image.name}` : "Upload ảnh bìa cho lớp học."}
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="class-schedule">
          Schedule
        </label>
        <Input
          id="class-schedule"
          value={draft.schedule}
          onChange={(event) => onChange({ schedule: event.target.value })}
          placeholder="Mon, Wed 09:00 - 11:00"
        />
      </div>

      {feedback ? (
        <div
          className={`rounded-2xl border px-4 py-3 text-sm ${
            feedback.tone === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-700"
              : "border-rose-200 bg-rose-50 text-rose-700"
          }`}
        >
          {feedback.message}
        </div>
      ) : null}

      <Button
        type="submit"
        className="w-full rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90"
        disabled={isCreating}
      >
        {isCreating ? (
          <>
            <LoaderCircle className="size-4 animate-spin" />
            Creating class...
          </>
        ) : (
          "Create class"
        )}
      </Button>
    </form>
  )
}
