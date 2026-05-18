import { MessageResponse } from "@/components/ai-elements/message"
import RecommendationRoadmap from "@/components/lms/RecommendationRoadmap"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import type { CodeReviewFeedback, UserRole } from "@/data/lms/extendedMockData"
import type { RecommendationResponse } from "@/store/redux/api/lmsApi"
import { LoaderCircle, Route } from "lucide-react"

export default function CodeReviewPanel({
  review,
  recommendationRoadmap,
  role,
  isRecommendationLoading,
  isRecommendationDialogOpen,
  onRecommendationDialogOpenChange,
  allowRecommendation = true,
}: {
  review: CodeReviewFeedback
  recommendationRoadmap: RecommendationResponse | null
  role: UserRole
  isRecommendationLoading: boolean
  isRecommendationDialogOpen: boolean
  onRecommendationDialogOpenChange: (open: boolean) => void
  allowRecommendation?: boolean
}) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-3">
          <CardTitle className="text-base text-[#030391]">
            AI Code Review
          </CardTitle>
          {allowRecommendation ? (
            <Button
              type="button"
              variant="outline"
              className="rounded-2xl border-[#1488D8]/20 text-[#1488D8] hover:bg-[#1488D8]/5 hover:text-[#1488D8]"
              onClick={() => onRecommendationDialogOpenChange(true)}
            >
              {isRecommendationLoading ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : (
                <Route className="size-4" />
              )}
              Xem gợi ý bài tập tiếp theo
            </Button>
          ) : null}
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

      <Card>
        <CardHeader>
          <CardTitle className="text-base text-[#030391]">
            Các nhận xét
          </CardTitle>
        </CardHeader>
        {review.reviewItems?.length ? (
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
        ) : (
          <CardContent>
            <div className="rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
              Chưa có nhận xét chi tiết cho bài này.
            </div>
          </CardContent>
        )}
      </Card>

      {allowRecommendation ? (
        <Dialog
          open={isRecommendationDialogOpen}
          onOpenChange={onRecommendationDialogOpenChange}
        >
          <DialogContent className="flex h-[88vh] max-h-[88vh] w-[min(96vw,72rem)] flex-col overflow-hidden p-0">
            <div className="grid min-h-0 flex-1 grid-rows-[auto_minmax(0,1fr)] overflow-hidden">
              <DialogHeader className="border-b border-slate-100 px-6 py-5">
                <DialogTitle>Lộ trình bài tập tiếp theo</DialogTitle>
                <DialogDescription>
                  Các bài luyện tập được gợi ý tiếp theo dựa trên bài hiện tại.
                </DialogDescription>
              </DialogHeader>

              <div className="min-h-0 overflow-y-auto overscroll-contain px-6 py-6">
                {isRecommendationLoading ? (
                  <div className="flex min-h-[24rem] flex-col items-center justify-center gap-3 text-center text-sm text-slate-500">
                    <LoaderCircle className="size-6 animate-spin text-[#1488D8]" />
                    <div>
                      <p className="font-medium text-slate-700">Đang tải lộ trình gợi ý</p>
                      <p className="mt-1">Vui lòng chờ trong giây lát.</p>
                    </div>
                  </div>
                ) : recommendationRoadmap ? (
                  <RecommendationRoadmap recommendation={recommendationRoadmap} role={role} />
                ) : (
                  <div className="flex min-h-[24rem] items-center justify-center rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                    Chưa có gợi ý bài tập tiếp theo cho bài này.
                  </div>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      ) : null}
    </div>
  )
}
