"use client"

import { GraduationCap, School } from "lucide-react"

import type { UserRole } from "@/data/lms/extendedMockData"
import { cn } from "@/lib/utils"

const options: {
  role: UserRole
  title: string
  description: string
  Icon: typeof School
}[] = [
  {
    role: "student",
    title: "Sinh viên",
    description: "Vào các khóa học đã đăng ký, làm bài tập lập trình và xem gợi ý học tập phù hợp.",
    Icon: GraduationCap,
  },
  {
    role: "lecturer",
    title: "Giảng viên",
    description: "Quản lý lớp học, xây dựng bài tập lập trình và theo dõi bài nộp của sinh viên.",
    Icon: School,
  },
]

export default function RoleSelector({
  value,
  onChange,
}: {
  value: UserRole
  onChange: (role: UserRole) => void
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {options.map(({ role, title, description, Icon }) => {
        const active = value === role

        return (
          <button
            key={role}
            type="button"
            onClick={() => onChange(role)}
            className={cn(
              "rounded-3xl border p-5 text-left transition-all",
              active
                ? "border-[#030391] bg-[#030391] text-white shadow-xl"
                : "border-white/70 bg-white/85 text-slate-900 hover:border-[#1488D8]/30 hover:bg-white"
            )}
          >
            <div className="mb-4 flex size-12 items-center justify-center rounded-2xl bg-white/15">
              <Icon className={cn("size-6", active ? "text-white" : "text-[#030391]")} />
            </div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className={cn("mt-2 text-sm", active ? "text-white/80" : "text-slate-600")}>
              {description}
            </p>
          </button>
        )
      })}
    </div>
  )
}
