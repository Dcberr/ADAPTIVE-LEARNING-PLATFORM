import type { CourseMaterial } from "@/data/lms/extendedMockData"
import type { EditableTestCase } from "@/components/lms/TestCaseManager"
import type { AssignmentDraft } from "@/components/lms/pages/lecturer-course-detail/types"
import type { ResourceDraft } from "@/components/lms/pages/lecturer-course-detail/ResourceModalForm"

export const classStatusClasses: Record<string, string> = {
  PLANNED: "bg-slate-100 text-slate-700 hover:bg-slate-100",
  IN_PROGRESS: "bg-sky-100 text-sky-700 hover:bg-sky-100",
  COMPLETED: "bg-emerald-100 text-emerald-700 hover:bg-emerald-100",
}

export const defaultDraftTests: EditableTestCase[] = [
  {
    id: "draft-test-1",
    input: "nums = [2, 7, 11, 15], target = 9",
    expectedOutput: "[0, 1]",
    hidden: false,
  },
  {
    id: "draft-test-2",
    input: "nums = [3, 2, 4], target = 6",
    expectedOutput: "[1, 2]",
    hidden: true,
  },
]

export const emptyResourceDraft: ResourceDraft = {
  topicId: "",
  title: "",
  type: "file" as CourseMaterial["type"],
  resourceUrl: "",
  fileSize: "",
  previewLabel: "",
}

export const emptyAssignmentDraft: AssignmentDraft = {
  id: "",
  topicId: "",
  title: "",
  description: "",
  difficulty: "Easy",
  score: "100",
  timeLimit: "45 phút",
  openAt: "",
  deadline: "",
  attemptsAllowed: "2",
  constraints: "",
  examples: "",
  topics: "",
  starterCode: {
    python: "def solve(nums, target):\n    pass",
    javascript: "function solve(nums, target) {\n  return []\n}",
    java: "class Solution {\n    public int[] solve(int[] nums, int target) {\n        return new int[]{};\n    }\n}",
    cpp: "#include <vector>\nusing namespace std;\n\nvector<int> solve(vector<int>& nums, int target) {\n    return {};\n}",
  },
  testCases: defaultDraftTests,
}

export function getClassStatusClassName(status: string) {
  return classStatusClasses[status] ?? "bg-violet-100 text-violet-700 hover:bg-violet-100"
}

export function formatClassDate(value: string) {
  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}
