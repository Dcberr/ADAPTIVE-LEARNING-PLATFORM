import Link from "next/link"
import {
  AlertCircle,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Play,
  Star,
  TrendingUp,
} from "lucide-react"

import { courses } from "@/data/lms/mockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

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

export default function DashboardPage() {
  const inProgress = courses.filter((course) => course.status === "in-progress")
  const featured = courses.find((course) => course.status === "featured")

  return (
    <div className="space-y-6">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#030391] to-[#1488D8] p-8 text-white shadow-2xl md:p-10">
        <div className="absolute right-0 top-0 h-96 w-96 translate-x-1/2 -translate-y-1/2 rounded-full bg-white/10 blur-3xl" />
        <div className="relative z-10">
          <div className="mb-3 flex items-center gap-2">
            <div className="size-3 animate-pulse rounded-full bg-[#FFD700]" />
            <span className="text-sm font-medium text-white/90">Chào mừng trở lại!</span>
          </div>
          <Badge className="mb-3 rounded-xl bg-white/20 px-3 py-1.5 text-sm text-white">
            Học kỳ 2, 2025-2026
          </Badge>
          <h2 className="mb-3 text-3xl font-bold md:text-4xl">Xin chào, Nguyễn Xuân Hiển!</h2>
          <p className="mb-6 max-w-2xl text-lg text-white/90">
            Bạn có 5 bài tập đang chờ và 4 sự kiện sắp tới trong tuần này.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/student/courses">
              <Button className="rounded-xl bg-white px-6 text-[#030391] hover:bg-white/90">
                <BookOpen className="mr-2 size-4" />
                Khóa học của tôi
              </Button>
            </Link>
            <Link href="/student/courses">
              <Button
                variant="outline"
                className="rounded-xl border-white/30 bg-white/10 px-6 text-white hover:bg-white/20"
              >
                Vào khóa học
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <div className="rounded-3xl border border-[#030391]/5 bg-white/70 p-6 shadow-lg backdrop-blur-xl">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#030391] to-[#1488D8]">
              <TrendingUp className="size-7 text-white" />
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-[#030391]">8</div>
              <p className="text-sm text-gray-500">Khóa học đang học</p>
            </div>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[#E3F2FD]">
            <div className="h-full w-full rounded-full bg-gradient-to-r from-[#030391] to-[#1488D8]" />
          </div>
        </div>

        <div className="rounded-3xl border border-[#1488D8]/5 bg-white/70 p-6 shadow-lg backdrop-blur-xl">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#1488D8] to-[#42A5F5]">
              <AlertCircle className="size-7 text-white" />
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-[#1488D8]">5</div>
              <p className="text-sm text-gray-500">Bài tập chờ nộp</p>
            </div>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[#E3F2FD]">
            <div className="h-full w-[62%] rounded-full bg-gradient-to-r from-[#1488D8] to-[#42A5F5]" />
          </div>
        </div>

        <div className="rounded-3xl border border-[#118B50]/5 bg-white/70 p-6 shadow-lg backdrop-blur-xl">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#118B50] to-[#0fa854]">
              <CheckCircle2 className="size-7 text-white" />
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-[#118B50]">90.2%</div>
              <p className="text-sm text-gray-500">Điểm trung bình</p>
            </div>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[#E8F8F0]">
            <div className="h-full w-[90%] rounded-full bg-gradient-to-r from-[#118B50] to-[#0fa854]" />
          </div>
        </div>
      </div>

      {featured ? (
        <div className="overflow-hidden rounded-3xl border border-[#030391]/5 bg-white/70 shadow-2xl backdrop-blur-xl">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="relative h-72 md:h-auto">
              <img src={courseImages[featured.image]} alt={featured.name} className="h-full w-full object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
              <Badge className="absolute right-4 top-4 bg-[#FFD700] px-4 py-1.5 font-bold text-[#030391]">
                <Star className="mr-1 size-4 fill-current" />
                Nổi bật
              </Badge>
            </div>
            <div className="flex flex-col justify-center p-8">
              <Badge className={`${featured.color} mb-3 w-fit text-white`}>{featured.code}</Badge>
              <h3 className="mb-3 text-2xl font-bold text-[#030391]">{featured.name}</h3>
              <p className="mb-6 text-gray-600">{featured.description}</p>
              <Link href={`/student/courses/${featured.id}`}>
                <Button className="w-full rounded-xl bg-gradient-to-br from-[#030391] to-[#1488D8] text-white">
                  <Play className="mr-2 size-4" />
                  Tiếp tục học
                </Button>
              </Link>
            </div>
          </div>
        </div>
      ) : null}

      <div className="rounded-3xl border border-[#030391]/5 bg-white/70 p-6 shadow-lg backdrop-blur-xl">
        <div className="mb-6 flex items-center justify-between">
          <h3 className="text-xl font-bold text-[#030391]">Khóa học đang học</h3>
          <Link href="/student/courses">
            <Button variant="ghost" size="sm" className="rounded-xl text-[#030391] hover:bg-[#E3F2FD]">
              Xem tất cả <ArrowRight className="ml-2 size-4" />
            </Button>
          </Link>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {inProgress.map((course) => (
            <Link key={course.id} href={`/student/courses/${course.id}`}>
              <div className="group overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-md transition-all hover:shadow-xl">
                <div className="relative h-40">
                  <img
                    src={courseImages[course.image]}
                    alt={course.name}
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                  <Badge className={`${course.color} absolute left-3 top-3 text-white`}>{course.code}</Badge>
                </div>
                <div className="p-4">
                  <h4 className="mb-2 line-clamp-2 text-sm font-semibold text-[#030391]">{course.name}</h4>
                  <p className="text-xs text-gray-500">{course.instructor}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
