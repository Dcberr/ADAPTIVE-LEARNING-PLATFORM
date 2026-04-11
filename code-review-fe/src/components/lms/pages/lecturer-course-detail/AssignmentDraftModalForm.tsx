"use client"

import TestCaseManager from "@/components/lms/TestCaseManager"
import type { AssignmentDraft } from "@/components/lms/pages/lecturer-course-detail/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"

const starterLanguages = ["python", "javascript", "java", "cpp"] as const

export default function AssignmentDraftModalForm({
  draft,
  isSubmitting,
  onChange,
  onCancel,
  onSave,
}: {
  draft: AssignmentDraft
  isSubmitting: boolean
  onChange: (patch: Partial<AssignmentDraft>) => void
  onCancel: () => void
  onSave: () => void
}) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <Input
          placeholder="Tiêu đề assignment"
          value={draft.title}
          onChange={(event) => onChange({ title: event.target.value })}
        />
        <select
          value={draft.difficulty}
          onChange={(event) =>
            onChange({ difficulty: event.target.value as AssignmentDraft["difficulty"] })
          }
          className="h-11 rounded-xl border bg-background px-3 text-sm"
        >
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
      </div>

      <Textarea
        rows={5}
        placeholder="Mô tả bài tập"
        value={draft.description}
        onChange={(event) => onChange({ description: event.target.value })}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Input
          placeholder="Điểm"
          value={draft.score}
          onChange={(event) => onChange({ score: event.target.value })}
        />
        <Input
          placeholder="Số lần làm bài"
          value={draft.attemptsAllowed}
          onChange={(event) => onChange({ attemptsAllowed: event.target.value })}
        />
        <Input
          placeholder="Thời gian làm bài"
          value={draft.timeLimit}
          onChange={(event) => onChange({ timeLimit: event.target.value })}
        />
        <Input
          placeholder="Chủ đề"
          value={draft.topics}
          onChange={(event) => onChange({ topics: event.target.value })}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Input
          placeholder="Ngày mở"
          type="datetime-local"
          value={draft.openAt}
          onChange={(event) => onChange({ openAt: event.target.value })}
        />
        <Input
          placeholder="Deadline"
          type="datetime-local"
          value={draft.deadline}
          onChange={(event) => onChange({ deadline: event.target.value })}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Textarea
          rows={5}
          placeholder="Constraints, mỗi dòng một điều kiện"
          value={draft.constraints}
          onChange={(event) => onChange({ constraints: event.target.value })}
        />
        <Textarea
          rows={5}
          placeholder="Examples, mô tả input/output cho sinh viên"
          value={draft.examples}
          onChange={(event) => onChange({ examples: event.target.value })}
        />
      </div>

      <div className="space-y-3">
        <p className="text-sm font-semibold text-[#030391]">Starter code</p>
        <Tabs defaultValue="python">
          <TabsList className="grid w-full grid-cols-4">
            {starterLanguages.map((language) => (
              <TabsTrigger key={language} value={language}>
                {language}
              </TabsTrigger>
            ))}
          </TabsList>

          {starterLanguages.map((language) => (
            <TabsContent key={language} value={language} className="pt-3">
              <Textarea
                rows={10}
                placeholder={`Starter code for ${language}`}
                value={draft.starterCode[language]}
                onChange={(event) =>
                  onChange({
                    starterCode: {
                      ...draft.starterCode,
                      [language]: event.target.value,
                    },
                  })
                }
              />
            </TabsContent>
          ))}
        </Tabs>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-semibold text-[#030391]">Test cases</p>
        <TestCaseManager
          value={draft.testCases}
          onChange={(testCases) => onChange({ testCases })}
        />
      </div>

      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Hủy
        </Button>
        <Button onClick={onSave} disabled={isSubmitting}>
          {isSubmitting ? "Đang tạo..." : "Lưu assignment"}
        </Button>
      </div>
    </div>
  )
}
