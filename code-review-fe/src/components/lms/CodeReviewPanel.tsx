import { CheckCircle2, ShieldAlert, Wrench } from "lucide-react"

import RecommendedProblems from "@/components/lms/RecommendedProblems"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type ReviewProblem = {
  id: string
  title: string
  difficulty: "Easy" | "Medium" | "Hard"
  topics: string[]
  estimatedMinutes: number
  solved: boolean
  reason: string
}

type ReviewFeedback = {
  strengths: string[]
  weaknesses: string[]
  improvements: string[]
}

export default function CodeReviewPanel({
  review,
  recommendedProblems,
}: {
  review: ReviewFeedback
  recommendedProblems: ReviewProblem[]
}) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base text-[#030391]">AI Code Review</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
            <div className="mb-3 flex items-center gap-2 font-semibold text-emerald-700">
              <CheckCircle2 className="size-4" />
              Strengths
            </div>
            <ul className="space-y-2 text-sm text-slate-700">
              {review.strengths.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-2xl border border-amber-100 bg-amber-50 p-4">
            <div className="mb-3 flex items-center gap-2 font-semibold text-amber-700">
              <ShieldAlert className="size-4" />
              Weaknesses
            </div>
            <ul className="space-y-2 text-sm text-slate-700">
              {review.weaknesses.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-2xl border border-sky-100 bg-sky-50 p-4">
            <div className="mb-3 flex items-center gap-2 font-semibold text-sky-700">
              <Wrench className="size-4" />
              Suggested improvements
            </div>
            <ul className="space-y-2 text-sm text-slate-700">
              {review.improvements.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      <RecommendedProblems problems={recommendedProblems} />
    </div>
  )
}
