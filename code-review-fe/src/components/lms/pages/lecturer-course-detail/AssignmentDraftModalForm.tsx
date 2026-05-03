"use client";

import Editor from "@monaco-editor/react";
import { Streamdown } from "streamdown";

import TestCaseManager from "@/components/lms/TestCaseManager";
import type { AssignmentDraft } from "@/components/lms/pages/lecturer-course-detail/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

function FieldBlock({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-2">
      <div>
        <p className="text-sm font-medium text-slate-800">{label}</p>
        {hint ? <p className="mt-1 text-xs text-slate-500">{hint}</p> : null}
      </div>
      {children}
    </label>
  );
}

function normalizeMarkdownInput(content: string) {
  return content
    .replace(/\\n/g, "\n")
    .replace(/^\s*<\/p>\s*/i, "")
    .replace(/\s*<p>\s*$/i, "")
    .replace(/<p>(?:&nbsp;|\s|<br\s*\/?>)*<\/p>/gi, "")
    .trim();
}

function MarkdownPreview({ content }: { content: string }) {
  return (
    <Streamdown
      mode="static"
      controls={false}
      components={{
        pre: ({ children, className, ...props }) => (
          <pre
            className={cn(
              "my-4 overflow-x-auto whitespace-pre-wrap border-l-4 border-slate-200 pl-4 font-mono text-[14px] leading-7 text-slate-600",
              className
            )}
            {...props}
          >
            {children}
          </pre>
        ),
        img: ({ alt, className, style, ...props }) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            alt={alt ?? ""}
            className={cn(
              "my-3 h-auto max-w-full rounded-xl border border-slate-200 bg-white",
              className
            )}
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
        [&_strong.example]:font-semibold
        [&_ul]:list-disc
        [&_ul]:pl-6
        [&_ol]:list-decimal
        [&_ol]:pl-6
      "
    >
      {normalizeMarkdownInput(content)}
    </Streamdown>
  );
}

function MarkdownEditorField({
  value,
  placeholder,
  rows,
  onChange,
}: {
  value: string;
  placeholder: string;
  rows: number;
  onChange: (value: string) => void;
}) {
  return (
    <Tabs defaultValue="write" className="gap-3">
      <TabsList className="grid w-full grid-cols-2 rounded-xl bg-slate-100 p-1">
        <TabsTrigger value="write" className="rounded-lg">
          Soạn thảo
        </TabsTrigger>
        <TabsTrigger value="preview" className="rounded-lg">
          Xem trước
        </TabsTrigger>
      </TabsList>
      <TabsContent value="write" className="mt-0">
        <Textarea
          rows={rows}
          placeholder={placeholder}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="min-h-[9rem] resize-y"
        />
      </TabsContent>
      <TabsContent value="preview" className="mt-0">
        <div className="min-h-[9rem] rounded-2xl border border-slate-200 bg-slate-50/60 px-4 py-3">
          {value.trim() ? (
            <MarkdownPreview content={value} />
          ) : (
            <p className="text-sm text-slate-400">
              Chưa có nội dung để xem trước.
            </p>
          )}
        </div>
      </TabsContent>
    </Tabs>
  );
}

export default function AssignmentDraftModalForm({
  draft,
  isSubmitting,
  onChange,
  onCancel,
  onSave,
}: {
  draft: AssignmentDraft;
  isSubmitting: boolean;
  onChange: (patch: Partial<AssignmentDraft>) => void;
  onCancel: () => void;
  onSave: () => void;
}) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <FieldBlock label="Tiêu đề bài tập">
          <Input
            placeholder="Ví dụ: Bài tập mảng 1 chiều"
            value={draft.title}
            onChange={(event) => onChange({ title: event.target.value })}
          />
        </FieldBlock>
        <FieldBlock label="Độ khó">
          <select
            value={draft.difficulty}
            onChange={(event) =>
              onChange({
                difficulty: event.target.value as AssignmentDraft["difficulty"],
              })
            }
            className="h-11 w-full rounded-xl border bg-background px-3 text-sm"
          >
            <option value="EASY">Easy</option>
            <option value="MEDIUM">Medium</option>
            <option value="HARD">Hard</option>
          </select>
        </FieldBlock>
      </div>

      <FieldBlock label="Mô tả bài toán">
        <MarkdownEditorField
          rows={7}
          placeholder="Nhập đề bài cho sinh viên..."
          value={draft.description}
          onChange={(value) => onChange({ description: value })}
        />
      </FieldBlock>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <FieldBlock label="Điểm số tối đa">
          <Input
            type="number"
            placeholder="Ví dụ: 100"
            value={draft.score}
            onChange={(event) => onChange({ score: event.target.value })}
          />
        </FieldBlock>
        <FieldBlock label="Số lần nộp">
          <Input
            type="number"
            placeholder="Ví dụ: 3"
            value={draft.attemptsAllowed}
            onChange={(event) =>
              onChange({ attemptsAllowed: event.target.value })
            }
          />
        </FieldBlock>
        <FieldBlock
          label="Time limit (phút)"
          hint="Số phút tối đa cho một lần làm bài."
        >
          <Input
            type="number"
            min="0"
            placeholder="Ví dụ: 90"
            value={draft.timeLimit}
            onChange={(event) => onChange({ timeLimit: event.target.value })}
          />
        </FieldBlock>
        <FieldBlock
          label="Tags"
          hint="Không bắt buộc. Nhập các tag, phân tách bằng dấu phẩy."
        >
          <Input
            placeholder="Ví dụ: array, loop"
            value={draft.tags}
            onChange={(event) => onChange({ tags: event.target.value })}
          />
        </FieldBlock>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <FieldBlock label="Thời điểm mở">
          <Input
            type="datetime-local"
            value={draft.openAt}
            onChange={(event) => onChange({ openAt: event.target.value })}
          />
        </FieldBlock>
        <FieldBlock label="Hạn nộp">
          <Input
            type="datetime-local"
            value={draft.deadline}
            onChange={(event) => onChange({ deadline: event.target.value })}
          />
        </FieldBlock>
      </div>

      <FieldBlock
        label="Ràng buộc"
        hint="Hỗ trợ markdown hoặc HTML từ đề bài nguồn, ví dụ danh sách ul/li, code inline."
      >
        <MarkdownEditorField
          rows={6}
          placeholder="Ví dụ: 1 ≤ n ≤ 10^5"
          value={draft.constraints}
          onChange={(value) => onChange({ constraints: value })}
        />
      </FieldBlock>

      <div className="space-y-3">
        <div>
          <p className="text-sm font-semibold text-[#030391]">Starter code</p>
          <p className="mt-1 text-xs text-slate-500">
            Mã khởi tạo mặc định cho bài nộp C++.
          </p>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200">
          <Editor
            height="320px"
            language="cpp"
            value={draft.functionSkeleton.cpp}
            onChange={(value) =>
              onChange({
                functionSkeleton: {
                  ...draft.functionSkeleton,
                  cpp: value ?? "",
                },
              })
            }
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbersMinChars: 3,
              scrollBeyondLastLine: false,
              wordWrap: "on",
              automaticLayout: true,
              tabSize: 2,
              padding: { top: 12, bottom: 12 },
            }}
          />
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm font-semibold text-[#030391]">Test cases</p>
          <p className="mt-1 text-xs text-slate-500">
            Khai báo input và output mong đợi cho hệ thống chấm bài.
          </p>
        </div>
        <TestCaseManager
          value={draft.testCases}
          onChange={(testCases) => onChange({ testCases })}
        />
      </div>

      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Hủy
        </Button>
        <Button onClick={onSave} disabled={isSubmitting}>
          {isSubmitting ? "Đang tạo..." : "Lưu assignment"}
        </Button>
      </div>
    </div>
  );
}
