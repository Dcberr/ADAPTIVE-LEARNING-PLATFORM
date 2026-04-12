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
    explanation: "Tổng của hai phần tử đầu tiên bằng target.",
    hidden: false,
  },
  {
    id: "draft-test-2",
    input: "nums = [3, 2, 4], target = 6",
    expectedOutput: "[1, 2]",
    explanation: "Cặp phần tử ở vị trí 1 và 2 tạo thành target.",
    hidden: true,
  },
]

export const emptyResourceDraft: ResourceDraft = {
  topicId: "",
  title: "",
  description: "",
  file: null,
}

export const emptyAssignmentDraft: AssignmentDraft = {
  id: "",
  topicId: "",
  title: "",
  description: "",
  difficulty: "EASY",
  score: "100",
  timeLimit: "90",
  openAt: "",
  deadline: "",
  attemptsAllowed: "2",
  constraints: "",
  tags: "",
  starterCode: {
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
