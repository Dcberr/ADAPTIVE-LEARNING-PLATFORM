"use client"

import Link from "next/link"
import { memo } from "react"
import {
  ChevronDown,
  ChevronRight,
  Download,
  ExternalLink,
  FilePenLine,
  Link2,
  MoreHorizontal,
  Plus,
  Trash2,
} from "lucide-react"

import MaterialIcon from "@/components/lms/pages/lecturer-course-detail/MaterialIcon"
import type { TopicCard } from "@/components/lms/pages/lecturer-course-detail/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type TopicSectionCardProps = {
  topic: TopicCard
  collapsed: boolean
  editMode: boolean
  onToggleTopic: (topicId: string) => void
  onEditTopic: (topicId: string) => void
  onDeleteTopic: (topicId: string) => void
  onDeleteMaterial: (materialId: string) => void
  onOpenResourceModal: (topicId: string, materialId?: string) => void
  onOpenAssignmentModal: (topicId: string) => void
  onEditAssignment: (assignmentId: string) => void
  onDeleteAssignment: (assignmentId: string) => void
  assignmentHrefPrefix?: string
}

function TopicSectionCardComponent({
  topic,
  collapsed,
  editMode,
  onToggleTopic,
  onEditTopic,
  onDeleteTopic,
  onDeleteMaterial,
  onOpenResourceModal,
  onOpenAssignmentModal,
  onEditAssignment,
  onDeleteAssignment,
  assignmentHrefPrefix,
}: TopicSectionCardProps) {
  const handleDownloadMaterial = async (title: string, resourceUrl: string) => {
    const response = await fetch(resourceUrl, {
      credentials: "include",
    })

    if (!response.ok) {
      throw new Error("Unable to download resource")
    }

    const blob = await response.blob()
    const objectUrl = window.URL.createObjectURL(blob)
    const link = document.createElement("a")

    link.href = objectUrl
    link.download = title
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(objectUrl)
  }

  const renderActionMenu = ({
    onEdit,
    onDelete,
  }: {
    onEdit: () => void
    onDelete: () => void
  }) => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon-sm"
          className="rounded-full text-slate-500 hover:bg-slate-100 hover:text-[#030391]"
        >
          <MoreHorizontal className="size-4" />
          <span className="sr-only">Mở menu thao tác</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" sideOffset={8}>
        <DropdownMenuItem onClick={onEdit}>
          <FilePenLine className="size-4" />
          Sửa
        </DropdownMenuItem>
        <DropdownMenuItem variant="destructive" onClick={onDelete}>
          <Trash2 className="size-4" />
          Xóa
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )

  return (
    <Card className="gap-0 overflow-hidden border border-slate-200 py-0 shadow-sm">
      <CardHeader className="space-y-0 p-4 sm:p-5">
        <div className="flex items-center justify-between gap-4">
          <div className="flex min-w-0 items-center gap-4">
            <button
              type="button"
              onClick={() => onToggleTopic(topic.id)}
              className="flex size-10 shrink-0 items-center justify-center rounded-full border border-slate-200 bg-slate-50 transition hover:bg-slate-100"
            >
              {collapsed ? (
                <ChevronRight className="size-4 text-[#1488D8]" />
              ) : (
                <ChevronDown className="size-4 text-[#1488D8]" />
              )}
            </button>

            <div className="min-w-0 flex-1">
              <CardTitle className="text-lg text-[#030391] sm:text-xl">{topic.title}</CardTitle>
              <p className="mt-1 line-clamp-2 text-sm text-slate-600">{topic.summary}</p>
            </div>
          </div>

          {editMode ? (
            <div className="flex shrink-0 items-center gap-2 self-start sm:self-center">
              <Button variant="outline" size="sm" className="rounded-xl" onClick={() => onEditTopic(topic.id)}>
                <FilePenLine className="size-4" />
                Sửa
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="rounded-xl border-rose-200 text-rose-600 hover:bg-rose-50 hover:text-rose-700"
                onClick={() => onDeleteTopic(topic.id)}
              >
                <Trash2 className="size-4" />
                Xóa
              </Button>
            </div>
          ) : null}
        </div>
      </CardHeader>

      {!collapsed ? (
        <CardContent className="border-t border-slate-100 p-5 sm:p-6">
          <div className="grid gap-5 lg:grid-cols-2">
            <div>
              <div className="mb-3 flex items-center justify-between gap-3">
                <p className="text-lg font-semibold text-[#030391]">Tài liệu</p>
                {editMode ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl"
                    onClick={() => onOpenResourceModal(topic.id)}
                  >
                    <Plus className="size-4" />
                    Thêm tài nguyên
                  </Button>
                ) : null}
              </div>

              <div className="space-y-3">
                {topic.materials.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                    Topic này chưa có tài liệu nào.
                  </div>
                ) : (
                  topic.materials.map((material) => (
                    <div
                      key={material.id}
                      className="flex items-center justify-between rounded-2xl border border-slate-200 p-4"
                    >
                      <div className="flex min-w-0 items-center gap-3">
                        <MaterialIcon type={material.type} />
                        <div className="min-w-0">
                          <a
                            href={material.resourceUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="block truncate text-sm font-medium text-slate-900 transition hover:text-[#1488D8]"
                          >
                            {material.title}
                          </a>
                        </div>
                      </div>

                      <div className="ml-3 flex shrink-0 items-center gap-1">
                        {editMode
                          ? renderActionMenu({
                              onEdit: () => onOpenResourceModal(topic.id, material.id),
                              onDelete: () => onDeleteMaterial(material.id),
                            })
                          : null}
                        <Button asChild variant="ghost" size="sm">
                          <a href={material.resourceUrl} target="_blank" rel="noreferrer">
                            <ExternalLink className="size-4" />
                          </a>
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            void handleDownloadMaterial(material.title, material.resourceUrl).catch(() => {
                              window.open(material.resourceUrl, "_blank", "noopener,noreferrer")
                            })
                          }}
                        >
                          <Download className="size-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div>
              <div className="mb-3 flex items-center justify-between gap-3">
                <p className="text-lg font-semibold text-[#030391]">Bài tập</p>
                {editMode ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl"
                    onClick={() => onOpenAssignmentModal(topic.id)}
                  >
                    <Plus className="size-4" />
                    Thêm bài tập
                  </Button>
                ) : null}
              </div>

              <div className="space-y-3">
                {topic.assignments.length === 0 && topic.customAssignments.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                    Topic này chưa có bài tập nào.
                  </div>
                ) : null}

                {topic.assignments.map((assignment) => {
                  const content = (
                    <div className="flex items-center justify-between rounded-2xl border border-[#1488D8]/15 bg-[#f8fbff] p-4 transition hover:border-[#1488D8]/40 hover:bg-white">
                      <div className="flex min-w-0 items-center gap-3">
                        <Link2 className="size-5 shrink-0 text-[#0f84c2]" />
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold text-[#030391]">
                            {assignment.title}
                          </p>
                          <p className="mt-1 text-xs text-slate-500">
                            {assignment.deadline
                              ? `Hạn nộp ${assignment.deadline} • ${assignment.difficulty}`
                              : assignment.difficulty}
                          </p>
                        </div>
                      </div>

                      {editMode ? (
                        <div className="ml-3 flex shrink-0 items-center gap-2">
                          {renderActionMenu({
                            onEdit: () => onEditAssignment(assignment.id),
                            onDelete: () => onDeleteAssignment(assignment.id),
                          })}
                        </div>
                      ) : (
                        <Badge variant="outline" className="ml-3 shrink-0">
                          Bài tập
                        </Badge>
                      )}
                    </div>
                  )

                  if (editMode) {
                    return <div key={assignment.id}>{content}</div>
                  }

                  return assignmentHrefPrefix ? (
                    <Link
                      key={assignment.id}
                      href={`${assignmentHrefPrefix}/${assignment.id}`}
                      className="block"
                    >
                      {content}
                    </Link>
                  ) : (
                    <div key={assignment.id}>{content}</div>
                  )
                })}

                {topic.customAssignments.map((assignment) => (
                  <div
                    key={assignment.id}
                    className="flex items-center justify-between rounded-2xl border border-slate-200 p-4"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <Link2 className="size-5 shrink-0 text-[#0f84c2]" />
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-[#030391]">
                          {assignment.title}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          Draft • {assignment.score} điểm • {assignment.timeLimit} •{" "}
                          {assignment.testCases.length} tests
                        </p>
                      </div>
                    </div>
                    <Badge className="ml-3 shrink-0 bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
                      Bài tập nháp
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      ) : null}
    </Card>
  )
}

function shallowStringArrayEqual(left: string[], right: string[]) {
  if (left.length !== right.length) {
    return false
  }

  return left.every((item, index) => item === right[index])
}

function areEqual(left: TopicSectionCardProps, right: TopicSectionCardProps) {
  if (left.collapsed !== right.collapsed || left.editMode !== right.editMode) {
    return false
  }

  if (left.assignmentHrefPrefix !== right.assignmentHrefPrefix) {
    return false
  }

  if (
    left.topic.id !== right.topic.id ||
    left.topic.title !== right.topic.title ||
    left.topic.summary !== right.topic.summary
  ) {
    return false
  }

  const leftMaterialKeys = left.topic.materials.map(
    (item) =>
      `${item.id}:${item.title}:${item.description}:${item.type}:${item.resourceUrl}:${item.fileSize}:${item.previewLabel}`
  )
  const rightMaterialKeys = right.topic.materials.map(
    (item) =>
      `${item.id}:${item.title}:${item.description}:${item.type}:${item.resourceUrl}:${item.fileSize}:${item.previewLabel}`
  )

  if (!shallowStringArrayEqual(leftMaterialKeys, rightMaterialKeys)) {
    return false
  }

  const leftAssignmentKeys = left.topic.assignments.map(
    (item) => `${item.id}:${item.title}:${item.deadline}:${item.difficulty}:${item.status}`
  )
  const rightAssignmentKeys = right.topic.assignments.map(
    (item) => `${item.id}:${item.title}:${item.deadline}:${item.difficulty}:${item.status}`
  )

  if (!shallowStringArrayEqual(leftAssignmentKeys, rightAssignmentKeys)) {
    return false
  }

  const leftDraftKeys = left.topic.customAssignments.map(
    (item) =>
      `${item.id}:${item.title}:${item.description}:${item.score}:${item.timeLimit}:${item.deadline}:${item.openAt}:${item.attemptsAllowed}:${item.constraints}:${item.tags}:${item.testCases.map((test) => `${test.input}:${test.expectedOutput}:${test.explanation}:${test.hidden}`).join("|")}`
  )
  const rightDraftKeys = right.topic.customAssignments.map(
    (item) =>
      `${item.id}:${item.title}:${item.description}:${item.score}:${item.timeLimit}:${item.deadline}:${item.openAt}:${item.attemptsAllowed}:${item.constraints}:${item.tags}:${item.testCases.map((test) => `${test.input}:${test.expectedOutput}:${test.explanation}:${test.hidden}`).join("|")}`
  )

  return shallowStringArrayEqual(leftDraftKeys, rightDraftKeys)
}

const TopicSectionCard = memo(TopicSectionCardComponent, areEqual)

export default TopicSectionCard
