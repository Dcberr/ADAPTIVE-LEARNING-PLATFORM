"use client"

import { useState } from "react"
import { Plus } from "lucide-react"

import type { ProblemBankEntry } from "@/data/lms/extendedMockData"
import ProblemBankTable from "@/components/lms/ProblemBankTable"
import SimpleModal from "@/components/lms/SimpleModal"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useLmsStore } from "@/store/lmsStore"

const emptyDraft = {
  title: "",
  description: "",
  difficulty: "Easy" as ProblemBankEntry["difficulty"],
  topics: "",
  estimatedMinutes: "30",
  recommendedForCourseIds: "",
  solvedByStudentIds: "",
  source: "lecturer" as ProblemBankEntry["source"],
}

export default function ProblemBankPage() {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [draft, setDraft] = useState(emptyDraft)
  const problems = useLmsStore((state) => state.problemBank)
  const saveProblem = useLmsStore((state) => state.saveProblem)

  const resetDraft = () => {
    setEditingId(null)
    setDraft(emptyDraft)
    setModalOpen(false)
  }

  const handleSave = () => {
    saveProblem(
      {
        title: draft.title,
        description: draft.description,
        difficulty: draft.difficulty,
        topics: draft.topics.split(",").map((item) => item.trim()).filter(Boolean),
        estimatedMinutes: Number(draft.estimatedMinutes),
        recommendedForCourseIds: draft.recommendedForCourseIds
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        solvedByStudentIds: draft.solvedByStudentIds
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        source: draft.source,
      },
      editingId ?? undefined
    )
    resetDraft()
  }

  const handleEdit = (problem: ProblemBankEntry) => {
    setEditingId(problem.id)
    setDraft({
      title: problem.title,
      description: problem.description,
      difficulty: problem.difficulty,
      topics: problem.topics.join(", "),
      estimatedMinutes: String(problem.estimatedMinutes),
      recommendedForCourseIds: problem.recommendedForCourseIds.join(", "),
      solvedByStudentIds: problem.solvedByStudentIds.join(", "),
      source: problem.source,
    })
    setModalOpen(true)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-2xl text-[#030391]">Problem Bank</CardTitle>
            <p className="mt-1 text-sm text-slate-500">
              Tạo, chỉnh sửa và gán các coding problem dùng chung cho khóa học.
            </p>
          </div>
          <Button
            className="rounded-2xl bg-[#1488D8] text-white hover:bg-[#1488D8]/90"
            onClick={() => {
              setEditingId(null)
              setDraft(emptyDraft)
              setModalOpen(true)
            }}
          >
            <Plus className="size-4" />
            Thêm bài vào kho
          </Button>
        </CardHeader>
        <CardContent>
          <ProblemBankTable problems={problems} onEdit={handleEdit} />
        </CardContent>
      </Card>

      <SimpleModal
        open={modalOpen}
        title={editingId ? "Chỉnh sửa bài trong kho" : "Thêm bài vào kho bài tập"}
        description="Popup này mô phỏng flow tạo problem tương tự popup thêm assignment."
        onClose={resetDraft}
      >
        <div className="space-y-4">
          <Input
            placeholder="Problem title"
            value={draft.title}
            onChange={(event) => setDraft((state) => ({ ...state, title: event.target.value }))}
          />
          <Textarea
            placeholder="Problem description"
            rows={5}
            value={draft.description}
            onChange={(event) =>
              setDraft((state) => ({ ...state, description: event.target.value }))
            }
          />
          <div className="grid gap-4 md:grid-cols-2">
            <select
              value={draft.difficulty}
              onChange={(event) =>
                setDraft((state) => ({
                  ...state,
                  difficulty: event.target.value as ProblemBankEntry["difficulty"],
                }))
              }
              className="h-11 rounded-xl border bg-background px-3 text-sm"
            >
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
            <Input
              placeholder="Estimated minutes"
              value={draft.estimatedMinutes}
              onChange={(event) =>
                setDraft((state) => ({ ...state, estimatedMinutes: event.target.value }))
              }
            />
          </div>
          <Input
            placeholder="Topics (comma separated)"
            value={draft.topics}
            onChange={(event) => setDraft((state) => ({ ...state, topics: event.target.value }))}
          />
          <Input
            placeholder="Recommended course IDs (comma separated)"
            value={draft.recommendedForCourseIds}
            onChange={(event) =>
              setDraft((state) => ({
                ...state,
                recommendedForCourseIds: event.target.value,
              }))
            }
          />
          <Input
            placeholder="Solved student IDs (comma separated)"
            value={draft.solvedByStudentIds}
            onChange={(event) =>
              setDraft((state) => ({ ...state, solvedByStudentIds: event.target.value }))
            }
          />
          <select
            value={draft.source}
            onChange={(event) =>
              setDraft((state) => ({
                ...state,
                source: event.target.value as ProblemBankEntry["source"],
              }))
            }
            className="h-11 rounded-xl border bg-background px-3 text-sm"
          >
            <option value="lecturer">Lecturer</option>
            <option value="bank">Bank</option>
          </select>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={resetDraft}>
              Hủy
            </Button>
            <Button onClick={handleSave}>
              {editingId ? "Cập nhật bài" : "Thêm bài vào kho"}
            </Button>
          </div>
        </div>
      </SimpleModal>
    </div>
  )
}
