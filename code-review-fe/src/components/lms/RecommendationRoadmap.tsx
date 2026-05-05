import Link from "next/link"
import { ArrowRight, BookOpenCheck, CircleDot, Route, Sparkles } from "lucide-react"

import type { UserRole } from "@/data/lms/extendedMockData"
import type { RecommendationResponse } from "@/store/redux/api/lmsApi"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

function getDifficultyLabel(value: string) {
  if (value === "HARD" || value === "Hard") return "Khó"
  if (value === "MEDIUM" || value === "Medium") return "Trung bình"
  return "Dễ"
}

function getDifficultyClass(value: string) {
  if (value === "HARD" || value === "Hard") {
    return "border-rose-200 bg-rose-50 text-rose-700"
  }

  if (value === "MEDIUM" || value === "Medium") {
    return "border-amber-200 bg-amber-50 text-amber-700"
  }

  return "border-emerald-200 bg-emerald-50 text-emerald-700"
}

export default function RecommendationRoadmap({
  recommendation,
  role,
}: {
  recommendation: RecommendationResponse | null
  role: UserRole
}) {
  if (!recommendation || recommendation.roadmap.length === 0) {
    return null
  }

  return (
    <Card className="border-[#1488D8]/15 bg-gradient-to-br from-[#f8fbff] via-white to-[#eef6ff]">
      <CardHeader className="gap-3 border-b border-[#1488D8]/10">
        <div className="flex items-center gap-2">
          <span className="flex size-9 items-center justify-center rounded-2xl bg-[#1488D8]/10 text-[#1488D8]">
            <Route className="size-4" />
          </span>
          <div>
            <CardTitle className="text-base text-[#030391]">
              Lộ trình bài tập tiếp theo
            </CardTitle>
            <CardDescription className="mt-1 text-slate-600">
              Gợi ý các bước luyện tập tiếp theo dựa trên bài hiện tại.
            </CardDescription>
          </div>
        </div>

        {recommendation.summary ? (
          <div className="rounded-2xl border border-[#1488D8]/10 bg-white/90 p-4">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 text-[#1488D8]">
                <Sparkles className="size-4" />
              </span>
              <p className="text-sm leading-6 text-slate-700">{recommendation.summary}</p>
            </div>
          </div>
        ) : null}
      </CardHeader>

      <CardContent className="space-y-5 pt-6">
        {recommendation.roadmap.map((step, index) => (
          <div key={step.step} className="relative pl-12">
            {index < recommendation.roadmap.length - 1 ? (
              <span className="absolute left-[18px] top-11 h-[calc(100%-1rem)] w-px bg-gradient-to-b from-[#1488D8]/30 to-transparent" />
            ) : null}

            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="absolute left-0 top-0 flex size-9 items-center justify-center rounded-2xl border border-[#1488D8]/20 bg-white text-sm font-semibold text-[#030391] shadow-sm transition hover:-translate-y-0.5 hover:border-[#1488D8]/40 hover:shadow"
                >
                  {step.step}
                </button>
              </TooltipTrigger>
              <TooltipContent side="right" className="max-w-xs px-3 py-2 text-left text-sm leading-6">
                {step.summary}
              </TooltipContent>
            </Tooltip>

            <div className="rounded-3xl border border-slate-200/80 bg-white/95 p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-[#030391]">Bước {step.step}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{step.summary}</p>
                </div>

                {step.target_concepts.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {step.target_concepts.map((concept) => (
                      <Badge
                        key={concept}
                        variant="outline"
                        className="rounded-full border-sky-200 bg-sky-50 px-3 py-1 text-sky-700"
                      >
                        {concept}
                      </Badge>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="mt-4 grid gap-3">
                {step.exercises.map((item) => (
                  <Tooltip key={`${step.step}-${item.priority}-${item.exercise.exercise_id}`}>
                    <TooltipTrigger asChild>
                      <Link
                        href={`/${role}/problem-bank/${item.exercise.exercise_id}`}
                        target="_blank"
                        rel="noreferrer"
                        className={cn(
                          "group flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 text-left transition",
                          "hover:-translate-y-0.5 hover:border-[#1488D8]/30 hover:bg-white hover:shadow-sm"
                        )}
                      >
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-[#030391]/8 text-xs font-semibold text-[#030391]">
                              {item.priority}
                            </span>
                            <span className="truncate text-sm font-medium text-slate-900 group-hover:text-[#030391]">
                              {item.exercise.title}
                            </span>
                          </div>

                          <div className="mt-2 flex flex-wrap items-center gap-2">
                            <Badge
                              variant="outline"
                              className={cn(
                                "rounded-full px-2.5 py-1 text-[11px]",
                                getDifficultyClass(item.exercise.difficulty)
                              )}
                            >
                              {getDifficultyLabel(item.exercise.difficulty)}
                            </Badge>

                            {item.exercise.concept_ids.slice(0, 3).map((concept) => (
                              <Badge
                                key={concept}
                                variant="outline"
                                className="rounded-full border-slate-200 bg-white px-2.5 py-1 text-[11px] text-slate-600"
                              >
                                {concept}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <div className="flex shrink-0 items-center gap-2 text-slate-400 transition group-hover:text-[#1488D8]">
                          <BookOpenCheck className="size-4" />
                          <ArrowRight className="size-4" />
                        </div>
                      </Link>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="max-w-sm px-3 py-2 text-left text-sm leading-6">
                      <div className="space-y-1">
                        <p className="font-semibold">Lý do gợi ý</p>
                        <p>{item.reason}</p>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                ))}
              </div>
            </div>
          </div>
        ))}

        {recommendation.focus_concept_ids.length > 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-200 bg-white/80 p-4">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <CircleDot className="size-4 text-[#1488D8]" />
              Khái niệm trọng tâm
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {recommendation.focus_concept_ids.map((concept) => (
                <Badge
                  key={concept}
                  variant="outline"
                  className="rounded-full border-[#1488D8]/20 bg-[#1488D8]/5 px-3 py-1 text-[#1488D8]"
                >
                  {concept}
                </Badge>
              ))}
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
