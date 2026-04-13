"use client";

import Editor from "@monaco-editor/react";

import TestCaseManager from "@/components/lms/TestCaseManager";
import type { AssignmentDraft } from "@/components/lms/pages/lecturer-course-detail/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

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
        <Textarea
          rows={5}
          placeholder="Nhập đề bài cho sinh viên..."
          value={draft.description}
          onChange={(event) => onChange({ description: event.target.value })}
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
        hint="Mỗi dòng một điều kiện, ví dụ giới hạn kích thước mảng hoặc phạm vi giá trị."
      >
        <Textarea
          rows={5}
          placeholder="Ví dụ: 1 ≤ n ≤ 10^5"
          value={draft.constraints}
          onChange={(event) => onChange({ constraints: event.target.value })}
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
