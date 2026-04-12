"use client"

import { useState } from "react"

import type { ProblemBankEntry } from "@/data/lms/extendedMockData"
import TestCaseManager, { type EditableTestCase } from "@/components/lms/TestCaseManager"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

type AssignmentDraft = {
  title: string
  description: string
  difficulty: "Easy" | "Medium" | "Hard"
  starterCode: string
  score: string
  timeLimit: string
  deadline: string
  topicId: string
}

const defaultTests: EditableTestCase[] = [
  {
    id: "draft-1",
    input: "nums = [2,7,11,15], target = 9",
    expectedOutput: "[0,1]",
    explanation: "Hai phần tử đầu tiên có tổng bằng target.",
    hidden: false,
  },
]

export default function AssignmentBuilder({
  availableProblems,
  onSave,
}: {
  availableProblems: ProblemBankEntry[]
  onSave: (draft: AssignmentDraft & { tests: EditableTestCase[] }) => void
}) {
  const [draft, setDraft] = useState<AssignmentDraft>({
    title: "",
    description: "",
    difficulty: "Easy",
    starterCode: "",
    score: "100",
    timeLimit: "2s",
    deadline: "",
    topicId: "",
  })
  const [tests, setTests] = useState<EditableTestCase[]>(defaultTests)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-[#030391]">Assignment Builder</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            placeholder="Title"
            value={draft.title}
            onChange={(event) => setDraft((state) => ({ ...state, title: event.target.value }))}
          />
          <select
            value={draft.difficulty}
            onChange={(event) =>
              setDraft((state) => ({
                ...state,
                difficulty: event.target.value as AssignmentDraft["difficulty"],
              }))
            }
            className="h-9 rounded-md border bg-background px-3 text-sm"
          >
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>
          <Input
            placeholder="Score"
            value={draft.score}
            onChange={(event) => setDraft((state) => ({ ...state, score: event.target.value }))}
          />
          <Input
            placeholder="Time limit"
            value={draft.timeLimit}
            onChange={(event) =>
              setDraft((state) => ({ ...state, timeLimit: event.target.value }))
            }
          />
          <Input
            placeholder="Deadline"
            type="datetime-local"
            value={draft.deadline}
            onChange={(event) =>
              setDraft((state) => ({ ...state, deadline: event.target.value }))
            }
          />
          <select
            value={draft.topicId}
            onChange={(event) => setDraft((state) => ({ ...state, topicId: event.target.value }))}
            className="h-9 rounded-md border bg-background px-3 text-sm"
          >
            <option value="">Attach to topic later</option>
            {availableProblems.map((problem) => (
              <option key={problem.id} value={problem.id}>
                Use bank idea: {problem.title}
              </option>
            ))}
          </select>
        </div>

        <Textarea
          placeholder="Description"
          rows={5}
          value={draft.description}
          onChange={(event) => setDraft((state) => ({ ...state, description: event.target.value }))}
        />

        <Textarea
          placeholder="Starter code"
          rows={8}
          value={draft.starterCode}
          onChange={(event) =>
            setDraft((state) => ({ ...state, starterCode: event.target.value }))
          }
        />

        <div>
          <p className="mb-3 text-sm font-medium text-[#030391]">Test cases</p>
          <TestCaseManager value={tests} onChange={setTests} />
        </div>

        <Button type="button" className="w-full" onClick={() => onSave({ ...draft, tests })}>
          Save assignment draft
        </Button>
      </CardContent>
    </Card>
  )
}
