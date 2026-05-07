"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  ChartNoAxesColumn,
  Users,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getLecturerCourses,
  getLecturerOverview,
} from "@/services/lms/mockLmsService";
import { useAppSelector } from "@/store/redux/hooks";

type LecturerOverview = Awaited<ReturnType<typeof getLecturerOverview>>;
type ManagedCourse = Awaited<ReturnType<typeof getLecturerCourses>>[number];

export default function LecturerDashboardPage() {
  const [overview, setOverview] = useState<LecturerOverview | null>(null);
  const [courses, setCourses] = useState<ManagedCourse[]>([]);
  const userName = useAppSelector(
    (state) => state.auth.user?.name ?? "Giảng viên",
  );

  useEffect(() => {
    getLecturerOverview().then(setOverview);
    getLecturerCourses().then(setCourses);
  }, []);

  return (
    <div className="space-y-6">
      {/* <div className="rounded-3xl bg-gradient-to-br from-[#030391] to-[#1488D8] p-8 text-white shadow-2xl">
        <Badge className="mb-4 rounded-full bg-white/15 px-3 py-1.5 text-white">
          Không gian giảng viên
        </Badge>
        <p className="text-sm font-medium text-white/85">Xin chào, {userName}!</p>
        <h1 className="mt-2 text-3xl font-bold">
          Quản lý lớp học lập trình thích ứng trên một bảng điều khiển duy nhất.
        </h1>
        <p className="mt-3 max-w-3xl text-white/80">
          Theo dõi kết quả học tập của sinh viên, quản lý kho bài tập, và giữ tài liệu cùng bài
          tập code bám sát từng topic trong lớp học.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/lecturer/courses">
            <Button className="rounded-xl bg-white text-[#030391] hover:bg-white/90">
              Mở lớp học đang quản lý
            </Button>
          </Link>
          <Link href="/lecturer/problem-bank">
            <Button
              variant="outline"
              className="rounded-xl border-white/30 bg-white/10 text-white hover:bg-white/20"
            >
              Mở Problem Bank
            </Button>
          </Link>
        </div>
      </div> */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#030391] to-[#1488D8] p-8 text-white shadow-2xl md:p-10">
        <div className="absolute right-0 top-0 h-96 w-96 translate-x-1/2 -translate-y-1/2 rounded-full bg-white/10 blur-3xl" />
        <div className="relative z-10">
          <div className="mb-3 flex items-center gap-2">
            <div className="size-3 animate-pulse rounded-full bg-[#0fa854]" />
            <span className="text-sm font-medium text-white/90">
              Chào mừng trở lại!
            </span>
          </div>
          <Badge className="mb-3 rounded-xl bg-white/20 px-3 py-1.5 text-sm text-white">
            Học kỳ 2, 2025-2026
          </Badge>
          <h2 className="mb-3 text-3xl font-bold md:text-4xl">
            Xin chào, {userName}!
          </h2>
          <p className="mb-6 max-w-2xl text-lg text-white/90">
            Theo dõi kết quả học tập của sinh viên, quản lý kho bài tập, và giữ
            tài liệu cùng bài tập code bám sát từng topic trong lớp học.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/lecturer/courses">
              <Button className="rounded-xl bg-white px-6 text-[#030391] hover:bg-white/90">
                <BookOpen className="mr-2 size-4" />
                Khóa học của tôi
              </Button>
            </Link>
            <Link href="/lecturer/problem-bank">
              <Button
                variant="outline"
                className="rounded-xl border-white/30 bg-white/10 px-6 text-white hover:bg-white/20"
              >
                Vào kho bài tập
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Lớp học đang quản lý</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">
                {overview?.managedCourses ?? "--"}
              </p>
            </div>
            <BookOpen className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Sinh viên đang theo dõi</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">
                {overview?.totalStudents ?? "--"}
              </p>
            </div>
            <Users className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Bài cần theo dõi thêm</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">
                {overview?.pendingReviews ?? "--"}
              </p>
            </div>
            <BrainCircuit className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-slate-500">Điểm trung bình lớp</p>
              <p className="mt-1 text-3xl font-bold text-[#030391]">
                {overview?.averageScore ?? "--"}%
              </p>
            </div>
            <ChartNoAxesColumn className="size-8 text-[#1488D8]" />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="w-full text-lg text-[#030391]">
            Lớp học đang quản lý
          </CardTitle>
          <Link href="/lecturer/courses">
            <Button variant="ghost" size="sm" className="text-[#030391]">
              Xem tất cả <ArrowRight className="size-4" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          {courses.map((course) => (
            <Link key={course.id} href={`/lecturer/courses/${course.id}`}>
              <div className="rounded-3xl border border-slate-200 bg-white p-5 transition hover:border-[#1488D8]/40 hover:shadow-lg">
                <Badge className={`${course.color} text-white`}>
                  {course.code}
                </Badge>
                <h3 className="mt-3 text-lg font-semibold text-[#030391]">
                  {course.name}
                </h3>
                <p className="mt-2 text-sm text-slate-600">
                  {course.description}
                </p>
                <p className="mt-3 text-xs text-slate-500">
                  {course.enrolled} sinh viên • tiến độ {course.progress}%
                </p>
              </div>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
