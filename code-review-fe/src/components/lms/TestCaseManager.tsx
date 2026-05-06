"use client"

import { Plus, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

export type EditableTestCase = {
  id: string
  input: string
  expectedOutput: string
  explanation: string
  hidden: boolean
}

export default function TestCaseManager({
  value,
  onChange,
}: {
  value: EditableTestCase[]
  onChange: (cases: EditableTestCase[]) => void
}) {
  const updateCase = (
    id: string,
    patch: Partial<EditableTestCase>
  ) => {
    onChange(value.map((testCase) => (testCase.id === id ? { ...testCase, ...patch } : testCase)))
  }

  const addCase = () => {
    onChange([
      ...value,
      {
        id: `test-${Date.now()}`,
        input: "",
        expectedOutput: "",
        explanation: "",
        hidden: false,
      },
    ])
  }

  const removeCase = (id: string) => {
    onChange(value.filter((testCase) => testCase.id !== id))
  }

  return (
    <div className="space-y-3">
      {value.map((testCase, index) => (
        <div key={testCase.id} className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="mb-3 flex items-center justify-between">
            <p className="font-medium text-[#030391]">Test case {index + 1}</p>
            <Button type="button" variant="ghost" size="sm" onClick={() => removeCase(testCase.id)}>
              <Trash2 className="size-4" />
            </Button>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <Textarea
              value={testCase.input}
              onChange={(event) => updateCase(testCase.id, { input: event.target.value })}
              placeholder="Input"
              rows={6}
              spellCheck={false}
              className="min-h-[50px] resize-y rounded-xl font-mono text-[13px] leading-6"
            />
            <Textarea
              value={testCase.expectedOutput}
              onChange={(event) =>
                updateCase(testCase.id, { expectedOutput: event.target.value })
              }
              placeholder="Expected output"
              rows={6}
              spellCheck={false}
              className="min-h-[50px] resize-y rounded-xl font-mono text-[13px] leading-6"
            />
          </div>
          <label className="mt-3 flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={testCase.hidden}
              onChange={(event) => updateCase(testCase.id, { hidden: event.target.checked })}
            />
            Hidden test case
          </label>
        </div>
      ))}

      <Button type="button" variant="outline" className="w-full" onClick={addCase}>
        <Plus className="size-4" />
        Add test case
      </Button>
    </div>
  )
}
