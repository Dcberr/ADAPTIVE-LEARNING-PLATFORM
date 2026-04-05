"use client"

import type { FormEvent } from "react"
import { LoaderCircle, Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

type FeedbackState =
  | {
      tone: "success" | "error"
      message: string
    }
  | null

export default function CreateClassCard({
  draft,
  feedback,
  isCreating,
  onChange,
  onSubmit,
}: {
  draft: {
    name: string
    description: string
  }
  feedback: FeedbackState
  isCreating: boolean
  onChange: (patch: Partial<{ name: string; description: string }>) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}) {
  return (
    <Card className="border border-slate-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl text-[#030391]">
          <Plus className="size-5 text-[#1488D8]" />
          Add class
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="class-name">
              Class name
            </label>
            <Input
              id="class-name"
              value={draft.name}
              onChange={(event) => onChange({ name: event.target.value })}
              placeholder="OOP K24 - Group 2"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="class-description">
              Description
            </label>
            <Textarea
              id="class-description"
              value={draft.description}
              onChange={(event) => onChange({ description: event.target.value })}
              placeholder="Describe the class scope or notes for this section."
            />
          </div>

          {feedback ? (
            <div
              className={`rounded-2xl border px-4 py-3 text-sm ${
                feedback.tone === "success"
                  ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                  : "border-rose-200 bg-rose-50 text-rose-700"
              }`}
            >
              {feedback.message}
            </div>
          ) : null}

          <Button
            type="submit"
            className="w-full rounded-xl bg-[#030391] text-white hover:bg-[#030391]/90"
            disabled={isCreating}
          >
            {isCreating ? (
              <>
                <LoaderCircle className="size-4 animate-spin" />
                Creating class...
              </>
            ) : (
              "Create class"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
