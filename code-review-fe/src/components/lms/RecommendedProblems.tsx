import { CheckCircle2, Circle, Clock3, Sparkles } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type RecommendedProblem = {
  id: string
  title: string
  difficulty: "Easy" | "Medium" | "Hard"
  topics: string[]
  estimatedMinutes: number
  solved: boolean
  reason: string
}

export default function RecommendedProblems({
  problems,
}: {
  problems: RecommendedProblem[]
}) {
  return (
    <Card className="border-emerald-100 bg-emerald-50/40">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base text-[#0f7a43]">
          <Sparkles className="size-4" />
          Recommended Next Exercises
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {problems.map((problem) => (
          <div key={problem.id} className="rounded-2xl border border-emerald-100 bg-white p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  {problem.solved ? (
                    <CheckCircle2 className="size-4 text-emerald-600" />
                  ) : (
                    <Circle className="size-4 text-slate-300" />
                  )}
                  <h4 className="font-semibold text-slate-900">{problem.title}</h4>
                </div>
                <p className="mt-2 text-sm text-slate-600">{problem.reason}</p>
              </div>
              <Badge variant="outline">{problem.difficulty}</Badge>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
              <span className="inline-flex items-center gap-1">
                <Clock3 className="size-3" />
                {problem.estimatedMinutes} mins
              </span>
              {problem.topics.map((topic) => (
                <Badge key={topic} className="bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
                  {topic}
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
