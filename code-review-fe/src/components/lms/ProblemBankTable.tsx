"use client"

import { useMemo, useState } from "react"
import { PencilLine, Search } from "lucide-react"

import type { ProblemBankEntry } from "@/data/lms/extendedMockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

export default function ProblemBankTable({
  problems,
  onEdit,
}: {
  problems: ProblemBankEntry[]
  onEdit: (problem: ProblemBankEntry) => void
}) {
  const [query, setQuery] = useState("")

  const filtered = useMemo(() => {
    const normalized = query.toLowerCase()

    return problems.filter((problem) =>
      `${problem.title} ${problem.description} ${problem.topics.join(" ")}`
        .toLowerCase()
        .includes(normalized)
    )
  }, [problems, query])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-[#030391]">Problem Bank</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="pl-10"
            placeholder="Search by title, description, or topic"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-slate-200 text-slate-500">
              <tr>
                <th className="py-3 pr-4">Title</th>
                <th className="py-3 pr-4">Difficulty</th>
                <th className="py-3 pr-4">Topics</th>
                <th className="py-3 pr-4">Source</th>
                <th className="py-3 pr-4">Recommended courses</th>
                <th className="py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((problem) => (
                <tr key={problem.id} className="border-b border-slate-100 align-top">
                  <td className="py-4 pr-4">
                    <p className="font-semibold text-slate-900">{problem.title}</p>
                    <p className="mt-1 max-w-md text-slate-500">{problem.description}</p>
                  </td>
                  <td className="py-4 pr-4">
                    <Badge variant="outline">{problem.difficulty}</Badge>
                  </td>
                  <td className="py-4 pr-4">
                    <div className="flex flex-wrap gap-2">
                      {problem.topics.map((topic) => (
                        <Badge key={topic} className="bg-[#E3F2FD] text-[#030391] hover:bg-[#E3F2FD]">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </td>
                  <td className="py-4 pr-4 capitalize text-slate-600">{problem.source}</td>
                  <td className="py-4 pr-4 text-slate-600">
                    {problem.recommendedForCourseIds.join(", ")}
                  </td>
                  <td className="py-4 text-right">
                    <Button type="button" variant="outline" size="sm" onClick={() => onEdit(problem)}>
                      <PencilLine className="size-4" />
                      Edit
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
