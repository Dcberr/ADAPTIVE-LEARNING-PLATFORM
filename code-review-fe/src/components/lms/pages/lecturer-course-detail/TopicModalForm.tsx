"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

export type TopicDraft = {
  title: string
  description: string
}

export default function TopicModalForm({
  draft,
  isSubmitting,
  onChange,
  onCancel,
  onSave,
}: {
  draft: TopicDraft
  isSubmitting: boolean
  onChange: (patch: Partial<TopicDraft>) => void
  onCancel: () => void
  onSave: () => void
}) {
  return (
    <div className="space-y-4">
      <Input
        placeholder="Tên section"
        value={draft.title}
        onChange={(event) => onChange({ title: event.target.value })}
      />
      <Textarea
        rows={5}
        placeholder="Mô tả nội dung của section"
        value={draft.description}
        onChange={(event) => onChange({ description: event.target.value })}
      />
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Hủy
        </Button>
        <Button onClick={onSave} disabled={isSubmitting}>
          {isSubmitting ? "Đang tạo..." : "Tạo section"}
        </Button>
      </div>
    </div>
  )
}
