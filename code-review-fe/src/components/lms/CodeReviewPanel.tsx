import { MessageResponse } from "@/components/ai-elements/message";
import RecommendedProblems from "@/components/lms/RecommendedProblems";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CodeReviewFeedback } from "@/data/lms/extendedMockData";

type ReviewProblem = {
  id: string;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  topics: string[];
  estimatedMinutes: number;
  solved: boolean;
  reason: string;
};

export default function CodeReviewPanel({
  review,
  recommendedProblems,
}: {
  review: CodeReviewFeedback;
  recommendedProblems: ReviewProblem[];
}) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base text-[#030391]">
            AI Code Review
          </CardTitle>
        </CardHeader>
        {review.summary ? (
          <CardContent className="space-y-3 border-b border-slate-100 pb-0">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-500">Tóm tắt</p>
              <MessageResponse className="mt-2 text-sm text-slate-700">
                {review.summary}
              </MessageResponse>
            </div>
          </CardContent>
        ) : null}
      </Card>

      {review.reviewItems?.length ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base text-[#030391]">
              Các nhận xét
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {review.reviewItems.map((item, index) => (
              <div
                key={`${item.issue}-${index}`}
                className="rounded-2xl border border-slate-200 p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold text-slate-900">
                    {item.type}
                  </span>
                  <span className="text-xs text-slate-500">
                    Dòng {item.line.start}-{item.line.end}
                  </span>
                </div>
                <MessageResponse className="mt-2 text-sm text-slate-700">
                  {item.issue}
                </MessageResponse>
                {item.fixSuggestion ? (
                  <div className="mt-2 text-sm text-sky-700">
                    <MessageResponse>{`Gợi ý:\n\n${item.fixSuggestion}`}</MessageResponse>
                  </div>
                ) : null}
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}

      <RecommendedProblems problems={recommendedProblems} />
    </div>
  );
}
