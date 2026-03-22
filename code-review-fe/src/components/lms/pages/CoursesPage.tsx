"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { Grid, List, Search } from "lucide-react"

import { courses } from "@/data/lms/mockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function CoursesPage() {
  const [query, setQuery] = useState("")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")

  const filtered = useMemo(() => {
    return courses.filter((course) => {
      const text = `${course.name} ${course.code} ${course.instructor}`.toLowerCase()
      return text.includes(query.toLowerCase())
    })
  }, [query])

  const renderGrid = (status?: string) => {
    const list = status ? filtered.filter((course) => course.status === status) : filtered

    if (viewMode === "list") {
      return (
        <div className="space-y-3">
          {list.map((course) => (
            <Link key={course.id} href={`/student/courses/${course.id}`}>
              <Card className="border border-[#005f69]/10 bg-white/80 transition hover:bg-white">
                <CardContent className="py-5">
                  <div className="mb-2 flex items-center justify-between">
                    <Badge className={`${course.color} text-white`}>{course.code}</Badge>
                    <span className="text-xs text-gray-500">{course.instructor}</span>
                  </div>
                  <h3 className="font-semibold text-[#005f69]">{course.name}</h3>
                  <p className="mt-2 text-sm text-gray-600">{course.description}</p>
                  <div className="mt-3">
                    <Progress value={course.progress} />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )
    }

    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {list.map((course) => (
          <Link key={course.id} href={`/student/courses/${course.id}`}>
            <Card className="h-full border border-[#005f69]/10 bg-white/80 transition hover:bg-white">
              <CardHeader>
                <div className="flex items-center justify-between gap-3">
                  <Badge className={`${course.color} text-white`}>{course.code}</Badge>
                  <span className="text-xs text-gray-500">{course.instructor}</span>
                </div>
                <CardTitle className="text-base text-[#005f69]">{course.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-3 text-sm text-gray-600">{course.description}</p>
                <Progress value={course.progress} />
                <p className="mt-2 text-xs text-gray-500">Tiến độ: {course.progress}%</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[#005f69]/5 bg-white/70 p-6 shadow-lg backdrop-blur-xl">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#005f69]">My Courses</h1>
            <p className="mt-1 text-sm text-gray-500">Track and manage your enrolled courses</p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === "grid" ? "default" : "outline"}
              size="icon"
              onClick={() => setViewMode("grid")}
              className={viewMode === "grid" ? "bg-[#005f69]" : ""}
            >
              <Grid className="size-4" />
            </Button>
            <Button
              variant={viewMode === "list" ? "default" : "outline"}
              size="icon"
              onClick={() => setViewMode("list")}
              className={viewMode === "list" ? "bg-[#005f69]" : ""}
            >
              <List className="size-4" />
            </Button>
          </div>
        </div>

        <div className="relative">
          <Search className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-gray-400" />
          <Input
            className="h-12 rounded-2xl border-none bg-[#f8f9fc] pl-12"
            placeholder="Search courses by name, code, or instructor..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
      </div>

      <Tabs defaultValue="all">
        <TabsList className="h-auto rounded-2xl border border-[#005f69]/5 bg-white/70 p-1.5 shadow-md">
          <TabsTrigger value="all" className="rounded-xl data-[state=active]:bg-[#005f69] data-[state=active]:text-white">
            All Courses ({filtered.length})
          </TabsTrigger>
          <TabsTrigger
            value="in-progress"
            className="rounded-xl data-[state=active]:bg-[#005f69] data-[state=active]:text-white"
          >
            In Progress ({filtered.filter((item) => item.status === "in-progress").length})
          </TabsTrigger>
          <TabsTrigger value="featured" className="rounded-xl data-[state=active]:bg-[#005f69] data-[state=active]:text-white">
            Featured ({filtered.filter((item) => item.status === "featured").length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-6">{renderGrid()}</TabsContent>
        <TabsContent value="in-progress" className="mt-6">{renderGrid("in-progress")}</TabsContent>
        <TabsContent value="featured" className="mt-6">{renderGrid("featured")}</TabsContent>
      </Tabs>
    </div>
  )
}
