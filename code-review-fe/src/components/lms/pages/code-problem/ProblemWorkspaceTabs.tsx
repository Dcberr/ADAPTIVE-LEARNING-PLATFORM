"use client"

import { memo } from "react"
import { LoaderCircle, Sparkles } from "lucide-react"

import type { CodeReviewFeedback } from "@/data/lms/extendedMockData"
import CodeReviewPanel from "@/components/lms/CodeReviewPanel"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { CodingProblem } from "@/data/lms/mockData"
import type { ExecutionSummary } from "@/services/lms/mockLmsService"

type ActiveTab = "description" | "testcases" | "result" | "review"

function ProblemWorkspaceTabsComponent({
  problem,
  activeTab,
  onTabChange,
  hasMounted,
  displayedExecution,
  review,
  recommendedProblems,
  runningAction,
  canRequestReview,
  onLoadReview,
}: {
  problem: CodingProblem
  activeTab: ActiveTab
  onTabChange: (tab: ActiveTab) => void
  hasMounted: (tab: ActiveTab) => boolean
  displayedExecution: ExecutionSummary | null
  review: CodeReviewFeedback | null
  recommendedProblems: Awaited<
    ReturnType<typeof import("@/services/lms/mockLmsService").getRecommendedProblems>
  >
  runningAction: "run" | "submit" | "review" | null
  canRequestReview: boolean
  onLoadReview: () => void
}) {
  const handleValueChange = (value: string) => {
    const nextTab = value as ActiveTab
    onTabChange(nextTab)
  }

  return (
    <Card className="min-h-[640px]">
      <CardHeader>
        <CardTitle className="text-base">Assignment Workspace</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={handleValueChange}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="description">Description</TabsTrigger>
            <TabsTrigger value="testcases">Test Cases</TabsTrigger>
            <TabsTrigger value="result">Result</TabsTrigger>
            <TabsTrigger value="review">Code Review</TabsTrigger>
          </TabsList>

          <TabsContent
            value="description"
            forceMount={hasMounted("description") ? true : undefined}
            hidden={activeTab !== "description"}
            className="space-y-4 pt-4"
          >
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <p className="whitespace-pre-line text-sm text-slate-700">{problem.description}</p>
            </div>

            <div>
              <h3 className="mb-3 text-sm font-semibold text-[#030391]">Constraints</h3>
              <div className="space-y-2">
                {problem.constraints.map((constraint) => (
                  <div key={constraint} className="rounded-xl border border-slate-200 p-3 text-sm">
                    {constraint}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-sm font-semibold text-[#030391]">Examples</h3>
              <div className="space-y-3">
                {problem.examples.map((example, index) => (
                  <div key={index} className="rounded-2xl border border-slate-200 p-4 text-sm">
                    <p>
                      <strong>Input:</strong> {example.input}
                    </p>
                    <p className="mt-2">
                      <strong>Output:</strong> {example.output}
                    </p>
                    {example.explanation ? (
                      <p className="mt-2 text-slate-600">
                        <strong>Explanation:</strong> {example.explanation}
                      </p>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
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
                  <strong>Input:</strong> {item.input}
                </p>
                <p className="mt-2">
                  <strong>Expected:</strong> {item.expectedOutput}
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
                      <p className="text-sm font-medium text-slate-500">Execution summary</p>
                      <p className="mt-1 text-2xl font-semibold text-[#030391]">
                        Passed: {displayedExecution.passed}/{displayedExecution.total}
                      </p>
                      <p className="mt-1 text-sm text-slate-500">
                        Score estimate: {displayedExecution.score} • {displayedExecution.percentage}% passing
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
                        View AI Code Review
                      </Button>
                    ) : (
                      <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100">
                        Reach 70% passing to unlock review
                      </Badge>
                    )}
                  </div>
                  <Progress className="mt-4" value={displayedExecution.percentage} />
                </div>

                <div className="space-y-3">
                  {displayedExecution.results.map((item) => (
                    <div key={item.idx} className="rounded-2xl border border-slate-200 p-4 text-sm">
                      <div className="flex items-center justify-between gap-3">
                        <p className={item.passed ? "text-emerald-600" : "text-rose-600"}>
                          Test {item.idx}: {item.passed ? "Passed" : "Failed"}
                        </p>
                        {item.hidden ? <Badge variant="outline">Hidden</Badge> : null}
                      </div>
                      <p className="mt-2 text-slate-600">Input: {item.input}</p>
                      <p className="mt-1 text-slate-600">Expected: {item.expected}</p>
                      <p className="mt-1 text-slate-600">Actual: {item.actual}</p>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                Run code to view visible test results here.
              </div>
            )}
          </TabsContent>

          <TabsContent
            value="review"
            forceMount={hasMounted("review") ? true : undefined}
            hidden={activeTab !== "review"}
            className="pt-4"
          >
            {review ? (
              <CodeReviewPanel review={review} recommendedProblems={recommendedProblems} />
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                {canRequestReview
                  ? "Use Review Code to generate AI feedback and personalized recommendations."
                  : "AI review unlocks after you pass at least 70% of the executed test cases."}
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
