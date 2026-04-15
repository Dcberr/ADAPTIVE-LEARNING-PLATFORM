import { memo } from "react"

import Editor from "@monaco-editor/react"
import { Code2, LoaderCircle, Play, Send, Sparkles } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function EditorWorkspaceCardComponent({
  language,
  code,
  runningAction,
  canRequestReview,
  readOnly = false,
  hideActions = false,
  helperTitle,
  helperLines,
  onCodeChange,
  onRun,
  onSubmit,
  onReview,
}: {
  language: string
  code: string
  runningAction: "run" | "submit" | "review" | null
  canRequestReview: boolean
  readOnly?: boolean
  hideActions?: boolean
  helperTitle?: string
  helperLines?: string[]
  onCodeChange: (value: string) => void
  onRun: () => void
  onSubmit: () => void
  onReview: () => void
}) {
  return (
    <Card className="min-h-[640px]">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Code2 className="size-4" /> Code Editor
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Editor
          height="450px"
          language={language === "cpp" ? "cpp" : language}
          value={code}
          onChange={(value) => onCodeChange(value ?? "")}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            readOnly,
            domReadOnly: readOnly,
            contextmenu: !readOnly,
          }}
        />
        {!hideActions ? (
          <div className="mt-4 grid gap-2 md:grid-cols-3">
            <Button onClick={onRun} variant="outline" disabled={runningAction !== null}>
              {runningAction === "run" ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : (
                <Play className="size-4" />
              )}
              Run Code
            </Button>
            <Button onClick={onSubmit} disabled={runningAction !== null}>
              {runningAction === "submit" ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
              Submit
            </Button>
            <Button
              onClick={onReview}
              variant="secondary"
              disabled={runningAction !== null || !canRequestReview}
            >
              {runningAction === "review" ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : (
                <Sparkles className="size-4" />
              )}
              Review Code
            </Button>
          </div>
        ) : null}

        <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          <p className="font-medium text-[#030391]">{helperTitle ?? "Submission flow"}</p>
          <ul className="mt-2 space-y-2">
            {(helperLines ?? [
              "Run Code executes the available sample tests and updates the Result tab.",
              "Submit saves the submission, score, elapsed time, and returns to the assignment page.",
              "Review Code becomes available after at least 70% of tests pass.",
            ]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}

const EditorWorkspaceCard = memo(EditorWorkspaceCardComponent)

export default EditorWorkspaceCard
