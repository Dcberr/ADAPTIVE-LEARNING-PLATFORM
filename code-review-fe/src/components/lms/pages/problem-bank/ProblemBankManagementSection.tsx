"use client"

import { useState } from "react"
import { MoreHorizontal, PencilLine, Plus, Trash2 } from "lucide-react"

import ConfirmActionModal from "@/components/lms/pages/lecturer-course-detail/ConfirmActionModal"
import ProblemBankTable from "@/components/lms/ProblemBankTable"
import type { UserRole } from "@/data/lms/extendedMockData"
import ProblemLibraryDraftForm, {
  EMPTY_PROBLEM_LIBRARY_DRAFT,
  type ProblemLibraryDraft,
} from "@/components/lms/pages/problem-bank/ProblemLibraryDraftForm"
import { normalizeFixedTagSlugs } from "@/components/lms/tagOptions"
import SimpleModal from "@/components/lms/SimpleModal"
import { useDebouncedValue } from "@/hooks/useDebouncedValue"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import CompactPagination from "@/components/ui/compact-pagination"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useToast } from "@/components/ui/toast-provider"
import type { EditableTestCase } from "@/components/lms/TestCaseManager"
import {
  type ProblemDetailResponse,
  useCreateLibraryProblemMutation,
  useDeleteLibraryProblemMutation,
  useGetProblemBankQuery,
  useLazyGetProblemByIdQuery,
  useUpdateLibraryProblemMutation,
} from "@/store/redux/api/lmsApi"

function toEditableTestcases(testcases: ProblemDetailResponse["testcases"]): EditableTestCase[] {
  return testcases.map((item, index) => ({
    id: item.id || `testcase-${index}`,
    input: item.input,
    expectedOutput: item.expectedOutput,
    explanation: item.explanation ?? "",
    hidden: item.hidden,
  }))
}

function toDraft(problem: ProblemDetailResponse): ProblemLibraryDraft {
  return {
    title: problem.title,
    description: problem.description,
    difficulty:
      problem.difficulty === "HARD" || problem.difficulty === "MEDIUM" || problem.difficulty === "EASY"
        ? problem.difficulty
        : "EASY",
    constraints: problem.problemConstraint ?? "",
    tags: normalizeFixedTagSlugs(problem.tags ?? []),
    starterCodes: {
      cpp: problem.functionSkeletons?.cpp ?? "",
    },
    testcases: toEditableTestcases(problem.testcases ?? []),
  }
}

function toPayload(draft: ProblemLibraryDraft) {
  return {
    title: draft.title.trim(),
    description: draft.description,
    difficulty: draft.difficulty,
    constraints: draft.constraints,
    starterCodes: {
      cpp: draft.starterCodes.cpp,
    },
    testcases: draft.testcases.map((item) => ({
      input: item.input,
      expectedOutput: item.expectedOutput,
      explanation: item.explanation.trim() || "",
      hidden: item.hidden,
    })),
    tags: normalizeFixedTagSlugs(draft.tags),
  }
}

function ProblemRowActions({
  problemId,
  onEdit,
  onDelete,
}: {
  problemId: string
  onEdit: (problemId: string) => void
  onDelete: (problemId: string) => void
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="size-9 rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-700"
          onClick={(event) => event.stopPropagation()}
        >
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" sideOffset={8}>
        <DropdownMenuItem
          onSelect={(event) => {
            event.preventDefault()
            onEdit(problemId)
          }}
        >
          <PencilLine className="size-4" />
          Sửa
        </DropdownMenuItem>
        <DropdownMenuItem
          variant="destructive"
          onSelect={(event) => {
            event.preventDefault()
            onDelete(problemId)
          }}
        >
          <Trash2 className="size-4" />
          Xóa
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default function ProblemBankManagementSection({
  role = "lecturer",
  canManage = true,
}: {
  role?: UserRole
  canManage?: boolean
}) {
  const { toast } = useToast()
  const [page, setPage] = useState(0)
  const [query, setQuery] = useState("")
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [editingProblemId, setEditingProblemId] = useState<string | null>(null)
  const [deletingProblemId, setDeletingProblemId] = useState<string | null>(null)
  const [draft, setDraft] = useState<ProblemLibraryDraft>(EMPTY_PROBLEM_LIBRARY_DRAFT)
  const debouncedQuery = useDebouncedValue(query)
  const size = 20

  const { data, isLoading, isFetching } = useGetProblemBankQuery({ page, size, q: debouncedQuery })
  const [getProblemById, { isFetching: isFetchingProblemDetail }] = useLazyGetProblemByIdQuery()
  const [createProblem, { isLoading: isCreating }] = useCreateLibraryProblemMutation()
  const [updateProblem, { isLoading: isUpdating }] = useUpdateLibraryProblemMutation()
  const [deleteProblem, { isLoading: isDeleting }] = useDeleteLibraryProblemMutation()

  const problems = data?.content ?? []
  const totalPages = data?.totalPages ?? 0
  const totalElements = data?.totalElements ?? 0
  const isTableLoading = isLoading || isFetching
  const isSubmitting = isCreating || isUpdating || isFetchingProblemDetail
  const isEditOpen = Boolean(editingProblemId)

  const deletingProblem = problems.find((problem) => problem.id === deletingProblemId) ?? null

  const handleQueryChange = (value: string) => {
    setQuery(value)
    setPage(0)
  }

  const closeCreateModal = () => {
    setIsCreateOpen(false)
    setDraft(EMPTY_PROBLEM_LIBRARY_DRAFT)
  }

  const closeEditModal = () => {
    setEditingProblemId(null)
    setDraft(EMPTY_PROBLEM_LIBRARY_DRAFT)
  }

  const handleOpenCreate = () => {
    setDraft(EMPTY_PROBLEM_LIBRARY_DRAFT)
    setIsCreateOpen(true)
  }

  const handleOpenEdit = async (problemId: string) => {
    try {
      const problem = await getProblemById(problemId).unwrap()
      setDraft(toDraft(problem))
      setEditingProblemId(problemId)
    } catch {
      toast({
        tone: "error",
        title: "Không tải được bài toán",
        description: "Không thể lấy dữ liệu chi tiết để chỉnh sửa bài trong kho.",
      })
    }
  }

  const handleCreate = async () => {
    try {
      await createProblem(toPayload(draft)).unwrap()
      toast({
        tone: "success",
        title: "Đã tạo bài mới",
        description: "Bài toán đã được thêm vào problem bank.",
      })
      closeCreateModal()
    } catch {
      toast({
        tone: "error",
        title: "Tạo bài thất bại",
        description: "Không thể tạo bài toán trong problem bank.",
      })
    }
  }

  const handleUpdate = async () => {
    if (!editingProblemId) return

    try {
      await updateProblem({
        problemId: editingProblemId,
        body: toPayload(draft),
      }).unwrap()
      toast({
        tone: "success",
        title: "Đã cập nhật bài toán",
        description: "Thông tin bài trong problem bank đã được lưu.",
      })
      closeEditModal()
    } catch {
      toast({
        tone: "error",
        title: "Cập nhật thất bại",
        description: "Không thể lưu thay đổi cho bài toán này.",
      })
    }
  }

  const handleDelete = async () => {
    if (!deletingProblemId) return

    try {
      await deleteProblem(deletingProblemId).unwrap()
      toast({
        tone: "success",
        title: "Đã xóa bài toán",
        description: "Bài toán đã được xóa khỏi problem bank.",
      })
      setDeletingProblemId(null)
    } catch {
      toast({
        tone: "error",
        title: "Xóa thất bại",
        description: "Không thể xóa bài toán này khỏi problem bank.",
      })
    }
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div>
            <CardTitle className="text-2xl text-[#030391]">Kho bài tập</CardTitle>
            <p className="mt-1 text-sm text-slate-500">
              {isTableLoading ? "Đang tải..." : `Tổng số bài: ${totalElements}`}
            </p>
          </div>

          {canManage ? (
            <Button
              type="button"
              className="rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90"
              onClick={handleOpenCreate}
            >
              <Plus className="size-4" />
              Thêm bài mới
            </Button>
          ) : null}
        </CardHeader>

        <CardContent>
          <ProblemBankTable
            problems={problems}
            isLoading={isTableLoading}
            page={page}
            size={size}
            query={query}
            onQueryChange={handleQueryChange}
            role={role}
            renderActions={
              canManage
                ? (problem) => (
                    <ProblemRowActions
                      problemId={problem.id}
                      onEdit={handleOpenEdit}
                      onDelete={setDeletingProblemId}
                    />
                  )
                : undefined
            }
          />

          <div className="mt-4 flex justify-center">
            <CompactPagination
              page={page}
              totalPages={totalPages}
              onPageChange={setPage}
              disabled={isFetching}
            />
          </div>
        </CardContent>
      </Card>

      {canManage ? (
        <>
          <SimpleModal
            open={isCreateOpen}
            title="Thêm bài mới vào Problem Bank"
            description="Tạo thủ công một bài luyện tập mới trong kho."
            onClose={closeCreateModal}
          >
            <ProblemLibraryDraftForm
              draft={draft}
              isSubmitting={isSubmitting}
              submitLabel="Lưu bài mới"
              submittingLabel="Đang tạo..."
              onChange={(patch) => setDraft((current) => ({ ...current, ...patch }))}
              onCancel={closeCreateModal}
              onSave={handleCreate}
            />
          </SimpleModal>

          <SimpleModal
            open={isEditOpen}
            title="Sửa bài trong Problem Bank"
            description="Cập nhật nội dung và test case của bài toán trong kho."
            onClose={closeEditModal}
          >
            <ProblemLibraryDraftForm
              draft={draft}
              isSubmitting={isSubmitting}
              submitLabel="Lưu thay đổi"
              submittingLabel="Đang cập nhật..."
              onChange={(patch) => setDraft((current) => ({ ...current, ...patch }))}
              onCancel={closeEditModal}
              onSave={handleUpdate}
            />
          </SimpleModal>

          <ConfirmActionModal
            open={Boolean(deletingProblemId)}
            title="Xóa bài trong Problem Bank"
            description={
              deletingProblem
                ? `Bạn sắp xóa bài "${deletingProblem.title}" khỏi kho bài tập.`
                : "Bạn sắp xóa một bài khỏi kho bài tập."
            }
            confirmLabel="Xóa bài"
            isSubmitting={isDeleting}
            onClose={() => setDeletingProblemId(null)}
            onConfirm={handleDelete}
          />
        </>
      ) : null}
    </>
  )
}
