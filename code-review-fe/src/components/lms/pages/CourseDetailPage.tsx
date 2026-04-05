"use client"

import { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import {
  ArrowLeft,
  BookOpen,
  Calendar,
  Download,
  FileText,
  ImageIcon,
  Video,
} from "lucide-react"

import { grades } from "@/data/lms/mockData"
import { useKeepAliveTabs } from "@/hooks/useKeepAliveTabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { getStudentCourseById, getStudentCourseTopics } from "@/services/lms/mockLmsService"

const courseImages: Record<string, string> = {
  "ai-digital-economy":
    "https://images.unsplash.com/photo-1655393001768-d946c97d6fd1?auto=format&fit=crop&w=1080&q=80",
  "fintech-blockchain":
    "https://images.unsplash.com/photo-1649359569078-c445b3c6a116?auto=format&fit=crop&w=1080&q=80",
  "design-thinking":
    "https://images.unsplash.com/photo-1562939651-9359f291c988?auto=format&fit=crop&w=1080&q=80",
  "algorithmic-trading":
    "https://images.unsplash.com/photo-1766218326892-4b261b02a03f?auto=format&fit=crop&w=1080&q=80",
  "marketing-analytics":
    "https://images.unsplash.com/photo-1599658880436-c61792e70672?auto=format&fit=crop&w=1080&q=80",
  "sustainable-business":
    "https://images.unsplash.com/photo-1741118843309-bbfe149f7b9e?auto=format&fit=crop&w=1080&q=80",
}

type TopicBundle = Awaited<ReturnType<typeof getStudentCourseTopics>>[number]
type CourseDetailTab = "topics" | "materials" | "assignments" | "grades"

function MaterialIcon({ type }: { type: TopicBundle["materials"][number]["type"] }) {
  if (type === "video") return <Video className="size-5 text-blue-600" />
  if (type === "image") return <ImageIcon className="size-5 text-purple-600" />
  return <FileText className="size-5 text-green-600" />
}

export default function CourseDetailPage({ courseId }: { courseId: string }) {
  const course = getStudentCourseById(courseId)
  const [topics, setTopics] = useState<TopicBundle[]>([])
  const { activeTab, handleTabChange, hasMounted } = useKeepAliveTabs<CourseDetailTab>("topics")

  useEffect(() => {
    getStudentCourseTopics(courseId).then(setTopics)
  }, [courseId])

  const courseGrade = grades.find((item) => item.courseId === courseId)

  const courseAssignments = useMemo(
    () =>
      topics.flatMap((topic) =>
        topic.assignments.map((assignment) => ({
          ...assignment,
          topicTitle: topic.title,
        }))
      ),
    [topics]
  )

  const allMaterials = useMemo(
    () => topics.flatMap((topic) => topic.materials.map((material) => ({ ...material, topicTitle: topic.title }))),
    [topics]
  )

  if (!course) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Course not found</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Link href="/student/courses">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="mr-2 size-4" /> Back to Courses
        </Button>
      </Link>

      <Card className="overflow-hidden">
        <div className="relative h-56">
          <img src={courseImages[course.image]} alt={course.name} className="h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
          <div className="absolute bottom-6 left-6 text-white">
            <Badge className={`${course.color} mb-2 text-white`}>{course.code}</Badge>
            <h1 className="text-3xl font-semibold">{course.name}</h1>
            <p className="mt-2 text-lg text-gray-200">{course.instructor}</p>
          </div>
        </div>
        <CardContent className="p-6">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-[1.2fr_0.8fr]">
            <div>
              <p className="text-sm text-gray-500">Schedule</p>
              <p className="mt-2 text-xl font-medium text-slate-900">{course.schedule}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Enrolled</p>
              <p className="mt-2 text-xl font-medium text-slate-900">{course.enrolled} students</p>
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
            <BookOpen className="mr-2 size-4" /> Topics
          </TabsTrigger>
          <TabsTrigger value="materials">
            <FileText className="mr-2 size-4" /> Materials ({allMaterials.length})
          </TabsTrigger>
          <TabsTrigger value="assignments">
            <Calendar className="mr-2 size-4" /> Assignments ({courseAssignments.length})
          </TabsTrigger>
          <TabsTrigger value="grades">Grades</TabsTrigger>
        </TabsList>

        <TabsContent
          value="topics"
          forceMount={hasMounted("topics") ? true : undefined}
          hidden={activeTab !== "topics"}
          className="mt-6 space-y-4"
        >
          {topics.map((topic) => (
            <Card key={topic.id}>
              <CardHeader>
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <CardTitle className="text-lg text-[#030391]">
                      Topic {topic.order}: {topic.title}
                    </CardTitle>
                    <p className="mt-2 text-sm text-slate-600">{topic.summary}</p>
                  </div>
                  <Badge variant="outline">{topic.assignments.length} assignments</Badge>
                </div>
              </CardHeader>
              <CardContent className="grid gap-5 lg:grid-cols-2">
                <div>
                  <p className="mb-3 text-sm font-semibold text-[#030391]">Learning materials</p>
                  <div className="space-y-3">
                    {topic.materials.map((material) => (
                      <div
                        key={material.id}
                        className="flex items-center justify-between rounded-2xl border border-gray-200 p-3"
                      >
                        <div className="flex items-center gap-3">
                          <MaterialIcon type={material.type} />
                          <div>
                            <p className="text-sm font-medium">{material.title}</p>
                            <p className="text-xs text-gray-500">
                              {material.previewLabel} • {material.fileSize}
                            </p>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Download className="size-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="mb-3 text-sm font-semibold text-[#030391]">Assignments</p>
                  <div className="space-y-3">
                    {topic.assignments.length === 0 ? (
                      <div className="rounded-2xl border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                        No assignments attached to this topic yet.
                      </div>
                    ) : (
                      topic.assignments.map((assignment) => (
                        <Link key={assignment.id} href={`/student/assignments/${assignment.id}`}>
                          <div className="rounded-2xl border border-[#1488D8]/15 bg-[#f8fbff] p-4 transition hover:border-[#1488D8]/40">
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <p className="font-semibold text-[#030391]">{assignment.title}</p>
                                <p className="mt-2 text-xs text-slate-500">
                                  Due {new Date(assignment.dueDate).toLocaleDateString("en-GB")} •{" "}
                                  {assignment.points} points
                                </p>
                              </div>
                              <Badge variant="outline">{assignment.difficulty ?? "Mixed"}</Badge>
                            </div>
                          </div>
                        </Link>
                      ))
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
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
                      {material.topicTitle} • {material.previewLabel} • {material.fileSize}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  Preview / Download
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
            <Link key={item.id} href={`/student/assignments/${item.id}`}>
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
                          Due: {new Date(item.dueDate).toLocaleDateString("en-GB")}
                        </span>
                        <span>{item.points} points</span>
                      </div>
                    </div>
                    <Badge variant="outline">{item.status}</Badge>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </TabsContent>

        <TabsContent
          value="grades"
          forceMount={hasMounted("grades") ? true : undefined}
          hidden={activeTab !== "grades"}
          className="mt-6"
        >
          <Card>
            <CardHeader>
              <CardTitle>Overall Grade</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className="text-5xl font-semibold text-green-600">
                  {courseGrade ? `${courseGrade.grade}%` : "N/A"}
                </div>
                <p className="mt-2 text-gray-500">Current Grade</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
