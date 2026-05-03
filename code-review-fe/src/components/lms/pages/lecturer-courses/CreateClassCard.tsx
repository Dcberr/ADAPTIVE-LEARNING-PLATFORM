"use client"

import { useEffect, useRef, type FormEvent } from "react"
import { LoaderCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

export default function CreateClassCard({
  draft,
  isCreating,
  submitLabel,
  submittingLabel,
  descriptionHint,
  onChange,
  onSubmit,
}: {
  draft: {
    name: string
    description: string
    image: File | null
    schedule: string
  }
  isCreating: boolean
  submitLabel?: string
  submittingLabel?: string
  descriptionHint?: string
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
          Tên lớp học
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
          Mô tả
        </label>
        <Textarea
          id="class-description"
          value={draft.description}
          onChange={(event) => onChange({ description: event.target.value })}
          placeholder="Mô tả ngắn nội dung, phạm vi hoặc ghi chú của lớp."
        />
        {descriptionHint ? <p className="text-xs text-slate-500">{descriptionHint}</p> : null}
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="class-image">
          Ảnh lớp học
        </label>
        <Input
          ref={fileInputRef}
          id="class-image"
          type="file"
          accept="image/*"
          onChange={(event) => onChange({ image: event.target.files?.[0] ?? null })}
        />
        <p className="text-xs text-slate-500">
          {draft.image ? `Selected: ${draft.image.name}` : "Có thể bỏ qua nếu chưa muốn thêm ảnh bìa."}
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="class-schedule">
          Lịch học
        </label>
        <Input
          id="class-schedule"
          value={draft.schedule}
          onChange={(event) => onChange({ schedule: event.target.value })}
          placeholder="Mon, Wed 09:00 - 11:00"
        />
      </div>

      <Button
        type="submit"
        className="w-full rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90"
        disabled={isCreating}
      >
        {isCreating ? (
          <>
            <LoaderCircle className="size-4 animate-spin" />
            {submittingLabel ?? "Đang tạo lớp..."}
          </>
        ) : (
          submitLabel ?? "Tạo lớp"
        )}
      </Button>
    </form>
  )
}
