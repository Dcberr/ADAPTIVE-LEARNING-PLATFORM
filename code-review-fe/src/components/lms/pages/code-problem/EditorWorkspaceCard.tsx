import { memo, useEffect, useRef } from "react"

import Editor from "@monaco-editor/react"
import { Code2, LoaderCircle, Play, Send, Sparkles } from "lucide-react"

import type { CodeReviewFeedback } from "@/data/lms/extendedMockData"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function EditorWorkspaceCardComponent({
  language,
  code,
  review,
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
  review?: CodeReviewFeedback | null
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
  const editorRef = useRef<any>(null)
  const monacoRef = useRef<any>(null)
  const decorationIdsRef = useRef<string[]>([])
  const hoverDisposableRef = useRef<any>(null)
  const reviewRef = useRef<CodeReviewFeedback | null | undefined>(review)

  const getHighlightedItems = () =>
    (reviewRef.current?.reviewItems ?? []).filter((item) => {
      const normalizedType = item.type.toLowerCase()
      return normalizedType === "warning" || normalizedType === "error"
    })

  const buildHoverContents = (item: NonNullable<CodeReviewFeedback["reviewItems"]>[number]) => {
    const contents = [
      { value: `**${item.type}**` },
      { value: `Line ${item.line.start}-${item.line.end}` },
      { value: item.issue },
    ]

    if (item.codeSnippet) {
      contents.push({ value: `Code snippet:\n\`\`\`${language}\n${item.codeSnippet}\n\`\`\`` })
    }

    if (item.fixSuggestion) {
      contents.push({ value: `Fix suggestion: ${item.fixSuggestion}` })
    }

    if (item.reviewLink?.relationSummary) {
      contents.push({ value: `History: ${item.reviewLink.relationSummary}` })
    }

    return contents
  }

  const applyDecorations = () => {
    const editor = editorRef.current
    const monaco = monacoRef.current

    if (!editor || !monaco) {
      return
    }

    const model = editor.getModel()
    if (!model) {
      return
    }

    const newDecorations = getHighlightedItems().flatMap((item) => {
      const className = item.type.toLowerCase() === "warning" ? "line-warning" : "line-error"
      const startLine = item.line.start
      const endLine = item.line.end
      const hoverMessage = buildHoverContents(item)
      const decorations = []

      for (let line = startLine; line <= endLine; line += 1) {
        const startColumn =
          line === startLine && item.column?.start && item.column.start > 0 ? item.column.start : 1
        let endColumn = model.getLineLastNonWhitespaceColumn(line)

        if (line === endLine && item.column?.end && item.column.end > 0) {
          endColumn = item.column.end
        }

        if (!endColumn || endColumn === 0) {
          endColumn = model.getLineMaxColumn(line)
        }

        decorations.push({
          range: new monaco.Range(line, startColumn, line, endColumn),
          options: {
            isWholeLine: false,
            className,
            hoverMessage,
          },
        })
      }

      return decorations
    })

    decorationIdsRef.current = editor.deltaDecorations(
      decorationIdsRef.current,
      newDecorations
    )
  }

  useEffect(() => {
    reviewRef.current = review
    requestAnimationFrame(() => {
      applyDecorations()
    })
  }, [review, code])

  useEffect(() => {
    return () => {
      if (hoverDisposableRef.current) {
        hoverDisposableRef.current.dispose()
      }
    }
  }, [])

  const handleMount = (editor: any, monaco: any) => {
    editorRef.current = editor
    monacoRef.current = monaco

    if (hoverDisposableRef.current) {
      hoverDisposableRef.current.dispose()
    }

    const normalizedLanguage = language === "cpp" ? "cpp" : language

    hoverDisposableRef.current = monaco.languages.registerHoverProvider(normalizedLanguage, {
      provideHover(model: any, position: any) {
        const item = getHighlightedItems().find((candidate) => {
          return (
            position.lineNumber >= candidate.line.start &&
            position.lineNumber <= candidate.line.end
          )
        })

        if (!item) {
          return null
        }

        const startLine = item.line.start
        const endLine = item.line.end
        const startColumn = item.column?.start && item.column.start > 0 ? item.column.start : 1
        const endColumn =
          item.column?.end && item.column.end > 0
            ? item.column.end
            : model.getLineMaxColumn(endLine)

        return {
          range: new monaco.Range(startLine, startColumn, endLine, endColumn),
          contents: buildHoverContents(item),
        }
      },
    })

    applyDecorations()
  }

  return (
    <Card className="min-h-[640px]">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Code2 className="size-4" /> Trình soạn thảo code
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Editor
          height="450px"
          language={language === "cpp" ? "cpp" : language}
          value={code}
          onChange={(value) => onCodeChange(value ?? "")}
          onMount={handleMount}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            readOnly,
            domReadOnly: readOnly,
            contextmenu: !readOnly,
            renderValidationDecorations: "off",
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
              Chạy code
            </Button>
            <Button onClick={onSubmit} disabled={runningAction !== null}>
              {runningAction === "submit" ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
              Nộp bài
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
              Code Review
            </Button>
          </div>
        ) : null}

        <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          <p className="font-medium text-[#030391]">{helperTitle ?? "Quy trình nộp bài"}</p>
          <ul className="mt-2 space-y-2">
            {(helperLines ?? [
              "Chạy code sẽ chạy các test mẫu hiện có và cập nhật tab Kết quả.",
              "Nộp bài sẽ lưu bài nộp, điểm số, thời gian làm và quay lại trang bài tập.",
              "Code Review sẽ mở sau khi đạt ít nhất 30% số test.",
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
