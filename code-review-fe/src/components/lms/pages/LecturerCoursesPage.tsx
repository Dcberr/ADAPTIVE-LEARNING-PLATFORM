"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight, Users } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getLecturerCourses } from "@/services/lms/mockLmsService"

type ManagedCourse = Awaited<ReturnType<typeof getLecturerCourses>>[number]

export default function LecturerCoursesPage() {
  const [courses, setCourses] = useState<ManagedCourse[]>([])

  useEffect(() => {
    getLecturerCourses().then(setCourses)
  }, [])

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-[#030391]">Managed Courses</CardTitle>
          <p className="text-sm text-slate-500">
            Open a course to manage topics, upload materials, configure coding assignments, and
            inspect student submissions.
          </p>
        </CardHeader>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {courses.map((course) => (
          <Card key={course.id} className="border border-slate-200">
            <CardContent className="p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <Badge className={`${course.color} text-white`}>{course.code}</Badge>
                  <h3 className="mt-3 text-xl font-semibold text-[#030391]">{course.name}</h3>
                  <p className="mt-2 text-sm text-slate-600">{course.description}</p>
                </div>
                <Users className="size-6 text-[#1488D8]" />
              </div>
              <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-500">
                <span>{course.enrolled} students</span>
                <span>Progress {course.progress}%</span>
                <span>{course.schedule}</span>
              </div>
              <Link href={`/lecturer/courses/${course.id}`}>
                <Button className="mt-5 rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90">
                  Open course <ArrowRight className="size-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
