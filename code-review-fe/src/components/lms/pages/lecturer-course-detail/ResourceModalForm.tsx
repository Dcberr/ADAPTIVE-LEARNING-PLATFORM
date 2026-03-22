"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { CourseMaterial } from "@/data/lms/extendedMockData"

export type ResourceDraft = {
  topicId: string
  title: string
  type: CourseMaterial["type"]
  resourceUrl: string
  fileSize: string
  previewLabel: string
}

export default function ResourceModalForm({
  draft,
  onChange,
  onCancel,
  onSave,
}: {
  draft: ResourceDraft
  onChange: (patch: Partial<ResourceDraft>) => void
  onCancel: () => void
  onSave: () => void
}) {
  return (
    <div className="space-y-4">
      <Input
        placeholder="Tên tài nguyên"
        value={draft.title}
        onChange={(event) => onChange({ title: event.target.value })}
      />
      <div className="grid gap-4 md:grid-cols-2">
        <select
          value={draft.type}
          onChange={(event) => onChange({ type: event.target.value as CourseMaterial["type"] })}
          className="h-11 rounded-xl border bg-background px-3 text-sm"
        >
          <option value="file">File</option>
          <option value="video">Video</option>
          <option value="image">Image</option>
        </select>
        <Input
          placeholder="Preview label"
          value={draft.previewLabel}
          onChange={(event) => onChange({ previewLabel: event.target.value })}
        />
      </div>
      <Input
        placeholder="Link tài nguyên"
        value={draft.resourceUrl}
        onChange={(event) => onChange({ resourceUrl: event.target.value })}
      />
      <Input
        placeholder="Kích thước / thời lượng"
        value={draft.fileSize}
        onChange={(event) => onChange({ fileSize: event.target.value })}
      />
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={onCancel}>
          Hủy
        </Button>
        <Button onClick={onSave}>Lưu tài nguyên</Button>
      </div>
    </div>
  )
}
