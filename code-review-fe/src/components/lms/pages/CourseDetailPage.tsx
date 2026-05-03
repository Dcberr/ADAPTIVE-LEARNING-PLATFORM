"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import {
  ArrowLeft,
  BookOpen,
  Calendar,
  FileText,
  ImageIcon,
  Video,
} from "lucide-react"

import { CourseDetailSkeleton } from "@/components/lms/LmsLoadingStates"
import { getClassCoverBackgroundImage } from "@/lib/class-cover"
import { getBackendBaseUrl } from "@/lib/auth"
import TopicSectionCard from "@/components/lms/pages/lecturer-course-detail/TopicSectionCard"
import type { TopicCard } from "@/components/lms/pages/lecturer-course-detail/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import {
  useGetClassByIdQuery,
  useGetClassTopicsQuery,
} from "@/store/redux/api/lmsApi"

type CourseDetailTab = "topics" | "materials" | "assignments"

type DisplayMaterial = {
  id: string
  title: string
  description: string
  topicTitle: string
  type: "file" | "video" | "image"
  previewLabel: string
  resourceUrl: string
}

type DisplayAssignment = {
  id: string
  title: string
  topicTitle: string
  deadline: string
  difficulty: string
  status: string
}

function MaterialIcon({ type }: { type: DisplayMaterial["type"] }) {
  if (type === "video") return <Video className="size-5 text-blue-600" />
  if (type === "image") return <ImageIcon className="size-5 text-purple-600" />
  return <FileText className="size-5 text-green-600" />
}

function normalizeMaterialType(value: string): DisplayMaterial["type"] {
  if (value === "video" || value === "image") {
    return value
  }

  return "file"
}

export default function CourseDetailPage({ courseId }: { courseId: string }) {
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<CourseDetailTab>("topics")
  const backendBaseUrl = getBackendBaseUrl()
  const [collapsedTopics, setCollapsedTopics] = useState<Record<string, boolean>>({})
  const {
    data: course,
    error: courseError,
    isLoading: isLoadingCourse,
  } = useGetClassByIdQuery(courseId)
  const {
    data: topicDetails = [],
    error: topicsError,
    isLoading: isLoadingTopics,
  } = useGetClassTopicsQuery(courseId)

  const allMaterials = useMemo<DisplayMaterial[]>(
    () =>
      topicDetails.flatMap((topic) =>
        topic.documents.map((material) => ({
          id: material.id,
          title: material.title,
          description: material.description,
          topicTitle: topic.title,
          type: normalizeMaterialType(material.type),
          previewLabel: material.type?.toUpperCase?.() ?? "FILE",
          resourceUrl: `${backendBaseUrl}/documents/download/${material.id}`,
        }))
      ),
    [backendBaseUrl, topicDetails]
  )

  const courseAssignments = useMemo<DisplayAssignment[]>(
    () =>
      topicDetails.flatMap((topic) =>
        topic.assignments.map((assignment) => ({
          id: assignment.id,
          title: assignment.title,
          topicTitle: topic.title,
          deadline: assignment.deadline,
          difficulty: assignment.difficulty,
          status: assignment.status,
        }))
      ),
    [topicDetails]
  )

  const topicCards = useMemo<TopicCard[]>(
    () =>
      topicDetails.map((topic, index) => ({
        id: topic.id,
        courseId,
        order: index + 1,
        title: topic.title,
        summary: topic.description,
        materials: topic.documents.map((material) => ({
          id: material.id,
          title: material.title,
          description: material.description,
          resourceUrl: `${backendBaseUrl}/documents/download/${material.id}`,
          type: normalizeMaterialType(material.type),
          fileSize: "",
          previewLabel: material.type?.toUpperCase?.() ?? "FILE",
        })),
        assignments: topic.assignments.map((assignment) => ({
          id: assignment.id,
          title: assignment.title,
          deadline: assignment.deadline,
          difficulty: assignment.difficulty,
          status: assignment.status,
        })),
        customAssignments: [],
      })),
    [backendBaseUrl, courseId, topicDetails]
  )

  if (isLoadingCourse) {
    return <CourseDetailSkeleton />
  }

  if (courseError || !course) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Không tìm thấy khóa học</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Link href="/student/courses">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="mr-2 size-4" /> Quay lại khóa học
        </Button>
      </Link>

      <Card className="overflow-hidden gap-0 py-0">
        <div
          className="relative h-56 bg-slate-100 bg-cover bg-center"
          style={{
            backgroundImage: getClassCoverBackgroundImage({
              seed: courseId,
              title: course.name,
              imageUrl: course.imageUrl,
            }),
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
          <div className="absolute bottom-6 left-6 text-white">
            <h1 className="text-3xl font-semibold">{course.name}</h1>
            <p className="mt-2 text-lg text-gray-200">{course.instructorName}</p>
          </div>
        </div>
        <CardContent className="p-6">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-[1.2fr_0.8fr]">
            <div>
              <p className="text-sm text-gray-500">Lịch học</p>
              <p className="mt-2 text-xl font-medium text-slate-900">
                {course.schedule ?? "Chưa cấu hình"}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Sinh viên tham gia</p>
              <p className="mt-2 text-xl font-medium text-slate-900">
                {course.enrolledStudentsCount} sinh viên
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs
        value={activeTab}
        onValueChange={(value) => handleTabChange(value as CourseDetailTab)}
        className="w-full"
      >
        <TabsList>
          <TabsTrigger value="topics">
            <BookOpen className="mr-2 size-4" /> Chủ đề
          </TabsTrigger>
          <TabsTrigger value="materials">
            <FileText className="mr-2 size-4" /> Tài liệu ({allMaterials.length})
          </TabsTrigger>
          <TabsTrigger value="assignments">
            <Calendar className="mr-2 size-4" /> Bài tập ({courseAssignments.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent
          value="topics"
          forceMount={hasMounted("topics") ? true : undefined}
          hidden={activeTab !== "topics"}
          className="mt-6 space-y-4"
        >
          {isLoadingTopics ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, index) => (
                <Card key={index}>
                  <CardContent className="space-y-4 p-6">
                    <Skeleton className="h-7 w-52 rounded-full" />
                    <Skeleton className="h-5 w-full rounded-full" />
                    <Skeleton className="h-5 w-2/3 rounded-full" />
                    <div className="grid gap-3 md:grid-cols-2">
                      <Skeleton className="h-24 rounded-3xl" />
                      <Skeleton className="h-24 rounded-3xl" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : topicsError ? (
            <Card>
              <CardContent className="p-6 text-sm text-rose-600">
                Không tải được nội dung khóa học.
              </CardContent>
            </Card>
          ) : topicDetails.length === 0 ? (
            <Card>
              <CardContent className="p-6 text-sm text-slate-500">
                Khóa học này chưa có topic nào.
              </CardContent>
            </Card>
          ) : (
            topicCards.map((topic) => (
              <TopicSectionCard
                key={topic.id}
                topic={topic}
                collapsed={Boolean(collapsedTopics[topic.id])}
                editMode={false}
                assignmentHrefPrefix="/student/assignments"
                onToggleTopic={(topicId) =>
                  setCollapsedTopics((state) => ({
                    ...state,
                    [topicId]: !state[topicId],
                  }))
                }
                onEditTopic={() => undefined}
                onDeleteTopic={() => undefined}
                onDeleteMaterial={() => undefined}
                onOpenResourceModal={() => undefined}
                onOpenAssignmentModal={() => undefined}
                onEditAssignment={() => undefined}
                onDeleteAssignment={() => undefined}
              />
            ))
          )}
        </TabsContent>

        <TabsContent
          value="materials"
          forceMount={hasMounted("materials") ? true : undefined}
          hidden={activeTab !== "materials"}
          className="mt-6 space-y-4"
        >
          {allMaterials.map((material) => (
            <Card key={material.id}>
              <CardContent className="flex items-center justify-between gap-4 p-5">
                <div className="flex items-center gap-3">
                  <MaterialIcon type={material.type} />
                  <div>
                    <p className="text-sm font-medium">{material.title}</p>
                    <p className="text-xs text-gray-500">
                      {material.topicTitle} • {material.previewLabel}
                    </p>
                  </div>
                </div>
                <Button asChild variant="outline" size="sm">
                  <a href={material.resourceUrl} target="_blank" rel="noreferrer">
                    Xem / tải
                  </a>
                </Button>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent
          value="assignments"
          forceMount={hasMounted("assignments") ? true : undefined}
          hidden={activeTab !== "assignments"}
          className="mt-6 space-y-3"
        >
          {courseAssignments.map((item) => (
            <Link key={item.id} href={`/student/assignments/${item.id}`} className="block">
              <Card className="transition hover:bg-slate-50">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-[#1488D8]">
                        {item.topicTitle}
                      </p>
                      <h3 className="mt-1 font-semibold">{item.title}</h3>
                      <div className="mt-2 flex items-center gap-3 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Calendar className="size-4" />
                          Hạn nộp: {new Date(item.deadline).toLocaleDateString("vi-VN")}
                        </span>
                        <span>{item.difficulty}</span>
                      </div>
                    </div>
                    <Badge variant="outline">{item.status}</Badge>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}
