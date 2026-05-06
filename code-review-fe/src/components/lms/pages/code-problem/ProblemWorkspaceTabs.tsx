"use client"

import { memo } from "react"
import { LoaderCircle, Sparkles } from "lucide-react"
import { Streamdown } from "streamdown"

import type { CodeReviewFeedback, UserRole } from "@/data/lms/extendedMockData"
import CodeReviewPanel from "@/components/lms/CodeReviewPanel"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { CodingProblem } from "@/data/lms/mockData"
import type { ExecutionSummary } from "@/services/lms/mockLmsService"
import type { RecommendationResponse } from "@/store/redux/api/lmsApi"
import { cn } from "@/lib/utils"

type ActiveTab = "description" | "testcases" | "result" | "review"

function normalizeRichText(content: string) {
  return content
    .replace(/\\n/g, "\n")
    .replace(/^\s*<\/p>\s*/i, "")
    .replace(/\s*<p>\s*$/i, "")
    .replace(/<p>(?:&nbsp;|\s|<br\s*\/?>)*<\/p>/gi, "")
    .trim()
}

function MarkdownBlock({ content }: { content: string }) {
  return (
    <Streamdown
      mode="static"
      controls={false}
      components={{
        pre: ({ children, className, ...props }) => (
          <pre
            className={cn(
              "my-4 overflow-x-auto whitespace-pre-wrap border-l-4 border-slate-200 pl-4 font-mono text-[15px] leading-8 text-slate-600",
              className
            )}
            {...props}
          >
            {children}
          </pre>
        ),
        img: ({ alt, className, style, ...props }) => (
          // Keep raw HTML image sizing from the source but normalize the surrounding look.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            alt={alt ?? ""}
            className={cn("my-3 h-auto max-w-full rounded-xl border border-slate-200 bg-white", className)}
            style={style}
            {...props}
          />
        ),
        p: ({ children, className, ...props }) => (
          <p className={cn("leading-7", className)} {...props}>
            {children}
          </p>
        ),
        ul: ({ children, className, ...props }) => (
          <ul className={cn("my-3 list-disc space-y-2 pl-6", className)} {...props}>
            {children}
          </ul>
        ),
        ol: ({ children, className, ...props }) => (
          <ol className={cn("my-3 list-decimal space-y-2 pl-6", className)} {...props}>
            {children}
          </ol>
        ),
        li: ({ children, className, ...props }) => (
          <li className={cn("leading-7 marker:text-slate-500", className)} {...props}>
            {children}
          </li>
        ),
        code: ({ children, className, ...props }) => (
          <code
            className={cn(
              "rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[0.95em] text-slate-800",
              className
            )}
            {...props}
          >
            {children}
          </code>
        ),
      }}
      className="
        text-sm text-slate-700
        [&_[data-streamdown='heading-1']]:mt-0
        [&_[data-streamdown='heading-2']]:mt-0
        [&_[data-streamdown='heading-3']]:mt-0
        [&_strong.example]:text-[15px]
        [&_strong.example]:font-semibold
        [&_p]:leading-6
        [&_ul]:list-disc
        [&_ul]:pl-6
        [&_ol]:list-decimal
        [&_ol]:pl-6
      "
    >
      {normalizeRichText(content)}
    </Streamdown>
  )
}

function ProblemWorkspaceTabsComponent({
  problem,
  activeTab,
  onTabChange,
  hasMounted,
  displayedExecution,
  review,
  recommendationRoadmap,
  role,
  isRecommendationLoading,
  isRecommendationDialogOpen,
  runningAction,
  canRequestReview,
  onLoadReview,
  onRecommendationDialogOpenChange,
  reviewEmptyMessage,
  showExamplesSection = false,
}: {
  problem: CodingProblem
  activeTab: ActiveTab
  onTabChange: (tab: ActiveTab) => void
  hasMounted: (tab: ActiveTab) => boolean
  displayedExecution: ExecutionSummary | null
  review: CodeReviewFeedback | null
  recommendationRoadmap: RecommendationResponse | null
  role: UserRole
  isRecommendationLoading: boolean
  isRecommendationDialogOpen: boolean
  runningAction: "run" | "submit" | "review" | null
  canRequestReview: boolean
  onLoadReview: () => void
  onRecommendationDialogOpenChange: (open: boolean) => void
  reviewEmptyMessage?: string
  showExamplesSection?: boolean
}) {
  const handleValueChange = (value: string) => {
    const nextTab = value as ActiveTab
    onTabChange(nextTab)
  }

  return (
    <Card className="min-h-[640px] min-w-0">
      <CardContent className="pt-6">
        <Tabs value={activeTab} onValueChange={handleValueChange}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="description">Mô tả</TabsTrigger>
            <TabsTrigger value="testcases">Test case</TabsTrigger>
            <TabsTrigger value="result">Kết quả</TabsTrigger>
            <TabsTrigger value="review">Code Review</TabsTrigger>
          </TabsList>

          <TabsContent
            value="description"
            forceMount={hasMounted("description") ? true : undefined}
            hidden={activeTab !== "description"}
            className="space-y-4 pt-4"
          >
            <div>
              <MarkdownBlock content={problem.description} />
            </div>

            {problem.problemConstraint ? (
              <div>
                <h3 className="mb-3 text-sm font-semibold text-[#030391]">Ràng buộc</h3>
                  <MarkdownBlock content={problem.problemConstraint} />
              </div>
            ) : null}

            {showExamplesSection ? (
              <div>
                <h3 className="mb-3 text-sm font-semibold text-[#030391]">Ví dụ</h3>
                <div className="space-y-3">
                  {problem.examples.map((example, index) => (
                    <div key={index} className="rounded-2xl border border-slate-200 p-4 text-sm">
                      <p>
                        <strong>Đầu vào:</strong> {example.input}
                      </p>
                      <p className="mt-2">
                        <strong>Đầu ra:</strong> {example.output}
                      </p>
                      {example.explanation ? (
                        <p className="mt-2 text-slate-600">
                          <strong>Giải thích:</strong> {example.explanation}
                        </p>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </TabsContent>

          <TabsContent
            value="testcases"
            forceMount={hasMounted("testcases") ? true : undefined}
            hidden={activeTab !== "testcases"}
            className="space-y-3 pt-4"
          >
            {problem.testCases.filter((item) => !item.hidden).map((item, index) => (
              <div key={index} className="rounded-2xl border border-slate-200 p-4 text-sm">
                <p>
                  <strong>Đầu vào:</strong> {item.input}
                </p>
                <p className="mt-2">
                  <strong>Kết quả mong đợi:</strong> {item.expectedOutput}
                </p>
              </div>
            ))}
          </TabsContent>

          <TabsContent
            value="result"
            forceMount={hasMounted("result") ? true : undefined}
            hidden={activeTab !== "result"}
            className="space-y-4 pt-4"
          >
            {displayedExecution ? (
              <>
                <div className="rounded-2xl border border-[#1488D8]/20 bg-[#f8fbff] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-slate-500">Tóm tắt lần chạy</p>
                      <p className="mt-1 text-2xl font-semibold text-[#030391]">
                        Đạt: {displayedExecution.passed}/{displayedExecution.total}
                      </p>
                      <p className="mt-1 text-sm text-slate-500">
                        Điểm ước tính: {displayedExecution.score} • {displayedExecution.percentage}% test đạt
                      </p>
                    </div>
                    {displayedExecution.eligibleForReview ? (
                      <Button
                        type="button"
                        className="rounded-2xl bg-emerald-600 text-white hover:bg-emerald-700"
                        onClick={onLoadReview}
                        disabled={runningAction === "review"}
                      >
                        {runningAction === "review" ? (
                          <LoaderCircle className="size-4 animate-spin" />
                        ) : (
                          <Sparkles className="size-4" />
                        )}
                        Xem AI Code Review
                      </Button>
                    ) : (
                      <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100">
                        Đạt 30% test để mở AI Code Review
                      </Badge>
                    )}
                  </div>
                  <Progress className="mt-4" value={displayedExecution.percentage} />
                </div>

                {displayedExecution.status === "COMPILE_ERROR" && displayedExecution.errorMessage ? (
                  <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4">
                    <p className="text-sm font-semibold text-rose-700">Lỗi biên dịch</p>
                    <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-xl bg-white/80 p-4 font-mono text-sm leading-6 text-rose-900">
                      {displayedExecution.errorMessage}
                    </pre>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {displayedExecution.results.map((item) => (
                      <div key={item.idx} className="rounded-2xl border border-slate-200 p-4 text-sm">
                        <div className="flex items-center justify-between gap-3">
                          <p className={item.passed ? "text-emerald-600" : "text-rose-600"}>
                            Test {item.idx}: {item.passed ? "Đạt" : "Trượt"}
                          </p>
                          {item.hidden ? <Badge variant="outline">Ẩn</Badge> : null}
                        </div>
                        <p className="mt-2 text-slate-600">Đầu vào: {item.input}</p>
                        <p className="mt-1 text-slate-600">Mong đợi: {item.expected}</p>
                        <p className="mt-1 text-slate-600">Thực tế: {item.actual}</p>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                Chạy code để xem kết quả các test hiển thị tại đây.
              </div>
            )}
          </TabsContent>

          <TabsContent
            value="review"
            forceMount={hasMounted("review") ? true : undefined}
            hidden={activeTab !== "review"}
            className="pt-4"
          >
            {runningAction === "review" && !review ? (
              <div className="flex min-h-[18rem] flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                <LoaderCircle className="size-5 animate-spin text-[#1488D8]" />
                <div>
                  <p className="font-medium text-slate-700">Vui lòng chờ review</p>
                  <p className="mt-1">Hệ thống đang phân tích bài làm và tạo nhận xét.</p>
                </div>
              </div>
            ) : review ? (
              <CodeReviewPanel
                review={review}
                recommendationRoadmap={recommendationRoadmap}
                role={role}
                isRecommendationLoading={isRecommendationLoading}
                isRecommendationDialogOpen={isRecommendationDialogOpen}
                onRecommendationDialogOpenChange={onRecommendationDialogOpenChange}
              />
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                {reviewEmptyMessage ??
                  (canRequestReview
                    ? "Dùng Code Review để tạo phản hồi AI và gợi ý cá nhân hóa."
                    : "AI Code Review sẽ mở sau khi bạn vượt qua ít nhất 30% số test đã chạy.")}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

const ProblemWorkspaceTabs = memo(ProblemWorkspaceTabsComponent)

export default ProblemWorkspaceTabs
