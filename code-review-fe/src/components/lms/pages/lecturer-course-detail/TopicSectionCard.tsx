"use client"

import { memo } from "react"
import { ChevronDown, ChevronRight, Download, ExternalLink, Link2, Plus, Trash2 } from "lucide-react"

import MaterialIcon from "@/components/lms/pages/lecturer-course-detail/MaterialIcon"
import type {
  AssignmentDraft,
  TopicCard,
} from "@/components/lms/pages/lecturer-course-detail/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

type TopicSectionCardProps = {
  topic: TopicCard
  collapsed: boolean
  editMode: boolean
  onToggleTopic: (topicId: string) => void
  onUpdateTopic: (topicId: string, patch: { title?: string; summary?: string }) => void
  onDeleteTopic: (topicId: string) => void
  onDeleteMaterial: (materialId: string) => void
  onOpenResourceModal: (topicId: string, materialId?: string) => void
  onOpenAssignmentModal: (topicId: string, draft?: AssignmentDraft) => void
  onDeleteDraftAssignment: (draftId: string) => void
}

function TopicSectionCardComponent({
  topic,
  collapsed,
  editMode,
  onToggleTopic,
  onUpdateTopic,
  onDeleteTopic,
  onDeleteMaterial,
  onOpenResourceModal,
  onOpenAssignmentModal,
  onDeleteDraftAssignment,
}: TopicSectionCardProps) {
  const getMaterialMeta = (description: string, previewLabel: string, fileSize: string) =>
    [description, previewLabel, fileSize].filter(Boolean).join(" • ")

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

  return (
    <Card className="overflow-hidden rounded-[2rem] border border-slate-200">
      <CardContent className="p-0">
        <div className="flex items-center justify-between gap-4 px-6 py-5">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => onToggleTopic(topic.id)}
              className="flex size-14 items-center justify-center rounded-full border border-slate-200 bg-slate-50"
            >
              {collapsed ? (
                <ChevronRight className="size-5 text-[#1488D8]" />
              ) : (
                <ChevronDown className="size-5 text-[#1488D8]" />
              )}
            </button>
            <div className="min-w-[280px]">
              {editMode ? (
                <div className="space-y-3">
                  <Input
                    value={topic.title}
                    onChange={(event) => onUpdateTopic(topic.id, { title: event.target.value })}
                  />
                  <Textarea
                    rows={2}
                    value={topic.summary}
                    onChange={(event) => onUpdateTopic(topic.id, { summary: event.target.value })}
                  />
                </div>
              ) : (
                <>
                  <h3 className="text-3xl font-bold text-[#1557d6]">{topic.title}</h3>
                  <p className="mt-2 text-sm text-slate-500">{topic.summary}</p>
                </>
              )}
            </div>
          </div>

          {editMode ? (
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="rounded-2xl text-rose-600"
                onClick={() => onDeleteTopic(topic.id)}
              >
                <Trash2 className="size-4" />
                Xóa
              </Button>
            </div>
          ) : null}
        </div>

        {!collapsed ? (
          <div className="border-t border-dashed border-slate-200 px-6 pb-6 pt-5">
            <div className="space-y-4">
              {topic.materials.map((material) => (
                <div
                  key={material.id}
                  className="flex items-center justify-between rounded-2xl border border-slate-200 px-5 py-4"
                >
                  <div className="flex items-center gap-4">
                    <MaterialIcon type={material.type} />
                    <div>
                      <a
                        href={material.resourceUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xl font-medium text-[#0f84c2] transition hover:text-[#1557d6] hover:underline"
                      >
                        {material.title}
                      </a>
                      <p className="mt-1 text-sm text-slate-500">
                        {getMaterialMeta(material.description, material.previewLabel, material.fileSize)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button asChild variant="outline" size="sm" className="rounded-xl">
                      <a href={material.resourceUrl} target="_blank" rel="noreferrer">
                        <ExternalLink className="size-4" />
                        Xem file
                      </a>
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="rounded-xl"
                      onClick={() => {
                        void handleDownloadMaterial(material.title, material.resourceUrl).catch(() => {
                          window.open(material.resourceUrl, "_blank", "noopener,noreferrer")
                        })
                      }}
                    >
                        <Download className="size-4" />
                        Tải xuống
                    </Button>
                    {editMode ? (
                      <>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onOpenResourceModal(topic.id, material.id)}
                      >
                        Sửa
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-rose-600"
                        onClick={() => onDeleteMaterial(material.id)}
                      >
                        Xóa
                      </Button>
                      </>
                    ) : (
                      <Badge variant="outline">Resource</Badge>
                    )}
                  </div>
                </div>
              ))}

              {topic.assignments.map((assignment) => (
                <div
                  key={assignment.id}
                  className="flex items-center justify-between rounded-2xl border border-slate-200 px-5 py-4"
                >
                  <div className="flex items-center gap-4">
                    <Link2 className="size-5 text-[#0f84c2]" />
                    <div>
                      <p className="text-xl font-medium text-[#0f84c2]">{assignment.title}</p>
                      <p className="mt-1 text-sm text-slate-500">
                        {assignment.difficulty}
                        {assignment.deadline ? ` • Deadline ${assignment.deadline}` : ""}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline">Assignment</Badge>
                </div>
              ))}

              {topic.customAssignments.map((assignment) => (
                <div
                  key={assignment.id}
                  className="flex items-center justify-between rounded-2xl border border-slate-200 px-5 py-4"
                >
                  <div className="flex items-center gap-4">
                    <Link2 className="size-5 text-[#0f84c2]" />
                    <div>
                      <p className="text-xl font-medium text-[#0f84c2]">{assignment.title}</p>
                      <p className="mt-1 text-sm text-slate-500">
                        Draft • {assignment.score} điểm • {assignment.timeLimit} •{" "}
                        {assignment.testCases.length} tests
                      </p>
                    </div>
                  </div>
                  {editMode ? (
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onOpenAssignmentModal(topic.id, assignment)}
                      >
                        Sửa
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-rose-600"
                        onClick={() => onDeleteDraftAssignment(assignment.id)}
                      >
                        Xóa
                      </Button>
                    </div>
                  ) : (
                    <Badge className="bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
                      Draft assignment
                    </Badge>
                  )}
                </div>
              ))}
            </div>

            {editMode ? (
              <div className="mt-6 flex justify-center">
                <div className="rounded-full border border-dashed border-[#7dc9eb] bg-[#d8f2fd] px-5 py-3">
                  <div className="flex flex-wrap items-center gap-3">
                    <Button
                      variant="ghost"
                      className="rounded-full text-[#0f658f] hover:bg-white/70"
                      onClick={() => onOpenResourceModal(topic.id)}
                    >
                      <Plus className="size-4" />
                      Thêm tài nguyên
                    </Button>
                    <Button
                      variant="ghost"
                      className="rounded-full text-[#0f658f] hover:bg-white/70"
                      onClick={() => onOpenAssignmentModal(topic.id)}
                    >
                      <Plus className="size-4" />
                      Thêm assignment
                    </Button>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        ) : null}
      </CardContent>
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

  if (left.topic.id !== right.topic.id || left.topic.title !== right.topic.title || left.topic.summary !== right.topic.summary) {
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
      `${item.id}:${item.title}:${item.description}:${item.score}:${item.timeLimit}:${item.deadline}:${item.openAt}:${item.attemptsAllowed}:${item.constraints}:${item.examples}:${item.topics}:${item.testCases.length}`
  )
  const rightDraftKeys = right.topic.customAssignments.map(
    (item) =>
      `${item.id}:${item.title}:${item.description}:${item.score}:${item.timeLimit}:${item.deadline}:${item.openAt}:${item.attemptsAllowed}:${item.constraints}:${item.examples}:${item.topics}:${item.testCases.length}`
  )

  return shallowStringArrayEqual(leftDraftKeys, rightDraftKeys)
}

const TopicSectionCard = memo(TopicSectionCardComponent, areEqual)

export default TopicSectionCard
