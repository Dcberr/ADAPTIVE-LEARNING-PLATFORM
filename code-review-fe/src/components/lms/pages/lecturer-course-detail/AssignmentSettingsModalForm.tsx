"use client"

import type { AssignmentSettingsDraft } from "@/components/lms/pages/lecturer-course-detail/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

function FieldBlock({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <label className="block space-y-2">
      <p className="text-sm font-medium text-slate-800">{label}</p>
      {children}
    </label>
  )
}

export default function AssignmentSettingsModalForm({
  draft,
  isSubmitting,
  onChange,
  onCancel,
  onSave,
}: {
  draft: AssignmentSettingsDraft
  isSubmitting: boolean
  onChange: (patch: Partial<AssignmentSettingsDraft>) => void
  onCancel: () => void
  onSave: () => void
}) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <FieldBlock label="Tiêu đề bài tập">
          <Input
            placeholder="Ví dụ: Bài tập mảng 1 chiều"
            value={draft.title}
            onChange={(event) => onChange({ title: event.target.value })}
          />
        </FieldBlock>

        <FieldBlock label="Độ khó">
          <select
            value={draft.difficulty}
            onChange={(event) =>
              onChange({
                difficulty: event.target.value as AssignmentSettingsDraft["difficulty"],
              })
            }
            className="h-11 w-full rounded-xl border bg-background px-3 text-sm"
          >
            <option value="EASY">Easy</option>
            <option value="MEDIUM">Medium</option>
            <option value="HARD">Hard</option>
          </select>
        </FieldBlock>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <FieldBlock label="Điểm số tối đa">
          <Input
            type="number"
            min="0"
            value={draft.score}
            onChange={(event) => onChange({ score: event.target.value })}
          />
        </FieldBlock>

        <FieldBlock label="Số lần nộp">
          <Input
            type="number"
            min="0"
            value={draft.attemptsAllowed}
            onChange={(event) => onChange({ attemptsAllowed: event.target.value })}
          />
        </FieldBlock>

        <FieldBlock label="Time limit (phút)">
          <Input
            type="number"
            min="0"
            value={draft.timeLimit}
            onChange={(event) => onChange({ timeLimit: event.target.value })}
          />
        </FieldBlock>

        <FieldBlock label="Tags">
          <Input
            placeholder="Ví dụ: array, loop"
            value={draft.tags}
            onChange={(event) => onChange({ tags: event.target.value })}
          />
        </FieldBlock>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <FieldBlock label="Thời điểm mở">
          <Input
            type="datetime-local"
            value={draft.openAt}
            onChange={(event) => onChange({ openAt: event.target.value })}
          />
        </FieldBlock>

        <FieldBlock label="Hạn nộp">
          <Input
            type="datetime-local"
            value={draft.deadline}
            onChange={(event) => onChange({ deadline: event.target.value })}
          />
        </FieldBlock>
      </div>

      <div className="rounded-2xl border border-sky-100 bg-sky-50/80 px-4 py-3 text-sm text-sky-900">
        API update assignment hiện chỉ lưu được metadata của bài tập. Phần đề bài, starter code,
        constraints và test case vẫn giữ nguyên ở màn tạo mới.
      </div>

      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Hủy
        </Button>
        <Button onClick={onSave} disabled={isSubmitting}>
          {isSubmitting ? "Đang lưu..." : "Lưu thay đổi"}
        </Button>
      </div>
    </div>
  )
}
