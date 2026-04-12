"use client"

import { useEffect, useRef } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

export type ResourceDraft = {
  topicId: string
  title: string
  description: string
  file: File | null
}

export default function ResourceModalForm({
  draft,
  isSubmitting,
  onChange,
  onCancel,
  onSave,
}: {
  draft: ResourceDraft
  isSubmitting: boolean
  onChange: (patch: Partial<ResourceDraft>) => void
  onCancel: () => void
  onSave: () => void
}) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!draft.file && fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }, [draft.file])

  return (
    <div className="space-y-4">
      <Input
        placeholder="Tên tài nguyên"
        value={draft.title}
        onChange={(event) => onChange({ title: event.target.value })}
      />
      <Textarea
        rows={4}
        placeholder="Mô tả tài nguyên"
        value={draft.description}
        onChange={(event) => onChange({ description: event.target.value })}
      />
      <div className="space-y-2">
        <Input
          ref={fileInputRef}
          type="file"
          onChange={(event) => onChange({ file: event.target.files?.[0] ?? null })}
        />
        <p className="text-xs text-slate-500">
          {draft.file ? `Selected: ${draft.file.name}` : "Chọn file tài nguyên để upload."}
        </p>
      </div>
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Hủy
        </Button>
        <Button onClick={onSave} disabled={isSubmitting}>
          {isSubmitting ? "Đang upload..." : "Lưu tài nguyên"}
        </Button>
      </div>
    </div>
  )
}
