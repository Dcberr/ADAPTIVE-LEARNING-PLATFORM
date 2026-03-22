"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  ChartNoAxesColumn,
  Users,
} from "lucide-react"

import { studentPerformance } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getLecturerCourses, getLecturerOverview } from "@/services/lms/mockLmsService"

type LecturerOverview = Awaited<ReturnType<typeof getLecturerOverview>>
type ManagedCourse = Awaited<ReturnType<typeof getLecturerCourses>>[number]

export default function LecturerDashboardPage() {
  const [overview, setOverview] = useState<LecturerOverview | null>(null)
  const [courses, setCourses] = useState<ManagedCourse[]>([])

  useEffect(() => {
    getLecturerOverview().then(setOverview)
    getLecturerCourses().then(setCourses)
  }, [])

  const atRisk = studentPerformance.filter((student) => student.status === "at-risk")

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-gradient-to-br from-[#030391] to-[#1488D8] p-8 text-white shadow-2xl">
        <Badge className="mb-4 rounded-full bg-white/15 px-3 py-1.5 text-white">
          Lecturer Workspace
        </Badge>
        <h1 className="text-3xl font-bold">Manage adaptive programming courses from one dashboard.</h1>
        <p className="mt-3 max-w-3xl text-white/80">
          Monitor student performance, create problem-bank entries, and keep course materials plus
          coding assignments aligned with each topic.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/lecturer/courses">
            <Button className="rounded-xl bg-white text-[#030391] hover:bg-white/90">
              Open managed courses
            </Button>
          </Link>
          <Link href="/lecturer/problem-bank">
            <Button
              variant="outline"
              className="rounded-xl border-white/30 bg-white/10 text-white hover:bg-white/20"
            >
              Open problem bank
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Managed courses</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">{overview?.managedCourses ?? "--"}</p>
            </div>
            <BookOpen className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Students tracked</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">{overview?.totalStudents ?? "--"}</p>
            </div>
            <Users className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Pending review follow-up</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">{overview?.pendingReviews ?? "--"}</p>
            </div>
            <BrainCircuit className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Average class score</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">{overview?.averageScore ?? "--"}%</p>
            </div>
            <ChartNoAxesColumn className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg text-[#030391]">Courses managed</CardTitle>
            <Link href="/lecturer/courses">
              <Button variant="ghost" size="sm" className="text-[#030391]">
                View all <ArrowRight className="size-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            {courses.map((course) => (
              <Link key={course.id} href={`/lecturer/courses/${course.id}`}>
                <div className="rounded-3xl border border-slate-200 bg-white p-5 transition hover:border-[#1488D8]/40 hover:shadow-lg">
                  <Badge className={`${course.color} text-white`}>{course.code}</Badge>
                  <h3 className="mt-3 text-lg font-semibold text-[#030391]">{course.name}</h3>
                  <p className="mt-2 text-sm text-slate-600">{course.description}</p>
                  <p className="mt-3 text-xs text-slate-500">
                    {course.enrolled} students • progress {course.progress}%
                  </p>
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-[#030391]">Students needing attention</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {atRisk.map((student) => (
              <div key={student.id} className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-[#030391]">{student.name}</p>
                    <p className="mt-1 text-sm text-slate-600">{student.email}</p>
                  </div>
                  <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100">
                    {student.averageScore}%
                  </Badge>
                </div>
                <p className="mt-3 text-xs text-slate-500">
                  Latest submission {new Date(student.lastSubmissionAt).toLocaleString("en-GB")}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
