import { CheckCircle2, ShieldAlert, Wrench } from "lucide-react"

import RecommendedProblems from "@/components/lms/RecommendedProblems"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { CodeReviewFeedback } from "@/data/lms/extendedMockData"

type ReviewProblem = {
  id: string
  title: string
  difficulty: "Easy" | "Medium" | "Hard"
  topics: string[]
  estimatedMinutes: number
  solved: boolean
  reason: string
}

export default function CodeReviewPanel({
  review,
  recommendedProblems,
}: {
  review: CodeReviewFeedback
  recommendedProblems: ReviewProblem[]
}) {
  const scorecardEntries = Object.entries(review.scorecard ?? {})

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base text-[#030391]">AI Code Review</CardTitle>
        </CardHeader>
        {review.summary || review.detail ? (
          <CardContent className="space-y-3 border-b border-slate-100 pb-0">
            {review.summary ? (
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-500">Summary</p>
                <p className="mt-2 text-sm text-slate-700">{review.summary}</p>
              </div>
            ) : null}
            {review.detail ? (
              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <p className="text-sm font-semibold text-slate-500">Detail</p>
                <p className="mt-2 whitespace-pre-line text-sm text-slate-700">{review.detail}</p>
              </div>
            ) : null}
          </CardContent>
        ) : null}
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

      {review.reviewItems?.length ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base text-[#030391]">Review Items</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {review.reviewItems.map((item, index) => (
              <div key={`${item.issue}-${index}`} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold text-slate-900">{item.type}</span>
                  <span className="text-xs text-slate-500">
                    Line {item.line.start}-{item.line.end}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-700">{item.issue}</p>
                {item.fixSuggestion ? (
                  <p className="mt-2 text-sm text-sky-700">Gợi ý: {item.fixSuggestion}</p>
                ) : null}
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}

      {scorecardEntries.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base text-[#030391]">Scorecard</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {scorecardEntries.map(([key, item]) => (
              <div key={key} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">{item.label || key}</p>
                <p className="mt-1 text-sm text-[#030391]">Score {item.score}</p>
                <p className="mt-2 text-sm text-slate-600">{item.explanation}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}

      <RecommendedProblems problems={recommendedProblems} />
    </div>
  )
}
