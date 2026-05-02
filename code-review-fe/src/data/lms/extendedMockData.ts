import { assignments, codingProblems, courses } from "@/data/lms/mockData"

export type UserRole = "student" | "lecturer"
export type MaterialType = "file" | "video" | "image"
export type SubmissionStatus = "submitted" | "reviewed"
export type StudentRiskStatus = "excelling" | "stable" | "at-risk"

export interface CourseMaterial {
  id: string
  topicId: string
  title: string
  type: MaterialType
  resourceUrl: string
  fileSize: string
  uploadedAt: string
  previewLabel: string
}

export interface CourseTopic {
  id: string
  courseId: string
  order: number
  title: string
  summary: string
  materialIds: string[]
  assignmentIds: string[]
}

export interface ExecutionTestResult {
  idx: number
  input: string
  expected: string
  actual: string
  passed: boolean
  hidden: boolean
}

export interface SubmissionRecord {
  id: string
  assignmentId: string
  startedAt: string
  submittedAt: string
  finishedAt: string
  durationSeconds: number
  language: "python" | "javascript" | "java" | "cpp"
  score: number
  passed: number
  total: number
  status: SubmissionStatus
  code: string
  testResults: ExecutionTestResult[]
}

export interface CodeReviewFeedback {
  assignmentId: string
  strengths: string[]
  weaknesses: string[]
  improvements: string[]
  summary?: string
  detail?: string
  reviewId?: string
  reviewItems?: Array<{
    line: {
      start: number
      end: number
    }
    column: {
      start: number
      end: number
    }
    type: string
    issue: string
    codeSnippet: string
    fixSuggestion: string
    reviewLink?: {
      currentIssue: string
      currentCodeSnippet: string
      previousSubmissionIndexes: number[]
      previousCodeSnippet: string
      whatImproved: string
      whatStillNeedsWork: string
      relationSummary: string
    } | null
  }>
  scorecard?: Record<
    string,
    {
      score: number
      label: string
      explanation: string
    }
  >
}

export interface ProblemBankEntry {
  id: string
  title: string
  description: string
  difficulty: "Easy" | "Medium" | "Hard" | "EASY" | "MEDIUM" | "HARD" | string
  topics: string[]
  estimatedMinutes: number
  recommendedForCourseIds: string[]
  solvedByStudentIds: string[]
  source: "bank" | "lecturer"
}

export interface StudentAssignmentScore {
  assignmentId: string
  assignmentTitle: string
  score: number
  submittedAt: string
}

export interface StudentPerformanceRecord {
  id: string
  name: string
  email: string
  courseId: string
  averageScore: number
  solvedProblems: number
  lastSubmissionAt: string
  status: StudentRiskStatus
  assignmentScores: StudentAssignmentScore[]
}

export const studentProfile = {
  id: "student-001",
  name: "Nguyen Xuan Hien",
  email: "student@bklearninghub.edu",
}

export const lecturerProfile = {
  id: "lecturer-001",
  name: "Dr. Tran Thi B",
  email: "lecturer@bklearninghub.edu",
}

export const courseTopics: CourseTopic[] = [
  {
    id: "topic-cs101-1",
    courseId: "1",
    order: 1,
    title: "Array Fundamentals And Hashing",
    summary: "Understand iteration, index lookup, and how hash maps reduce brute-force complexity.",
    materialIds: ["material-cs101-1", "material-cs101-2", "material-cs101-3"],
    assignmentIds: ["1", "4"],
  },
  {
    id: "topic-cs101-2",
    courseId: "1",
    order: 2,
    title: "Functions, Testing, And Debugging",
    summary: "Practice decomposing logic into functions and checking correctness with sample and hidden tests.",
    materialIds: ["material-cs101-4", "material-cs101-5"],
    assignmentIds: [],
  },
  {
    id: "topic-cs102-1",
    courseId: "2",
    order: 1,
    title: "Trees And Recursive Traversal",
    summary: "Model hierarchical data structures and reason about node insertion, search, and recursion depth.",
    materialIds: ["material-cs102-1", "material-cs102-2"],
    assignmentIds: ["2", "8"],
  },
  {
    id: "topic-cs102-2",
    courseId: "2",
    order: 2,
    title: "Sorting Strategies",
    summary: "Compare divide-and-conquer sorting approaches and analyze time and space complexity.",
    materialIds: ["material-cs102-3", "material-cs102-4"],
    assignmentIds: ["8"],
  },
  {
    id: "topic-cs201-1",
    courseId: "5",
    order: 1,
    title: "Component State And Effects",
    summary: "Build interactive client components and manage asynchronous UI states cleanly.",
    materialIds: ["material-cs201-1", "material-cs201-2"],
    assignmentIds: ["5"],
  },
  {
    id: "topic-cs202-1",
    courseId: "6",
    order: 1,
    title: "API Integration In Mobile Apps",
    summary: "Connect UI to remote services, model loading states, and normalize response handling.",
    materialIds: ["material-cs202-1", "material-cs202-2"],
    assignmentIds: ["7"],
  },
]

export const courseMaterials: CourseMaterial[] = [
  {
    id: "material-cs101-1",
    topicId: "topic-cs101-1",
    title: "Slides: Arrays And Indexed Access",
    type: "file",
    resourceUrl: "/materials/cs101-arrays.pdf",
    fileSize: "2.4 MB",
    uploadedAt: "2026-01-08T09:00:00",
    previewLabel: "PDF",
  },
  {
    id: "material-cs101-2",
    topicId: "topic-cs101-1",
    title: "Video: Two Sum Walkthrough",
    type: "video",
    resourceUrl: "https://video.example.com/two-sum",
    fileSize: "16:32",
    uploadedAt: "2026-01-09T09:00:00",
    previewLabel: "MP4",
  },
  {
    id: "material-cs101-3",
    topicId: "topic-cs101-1",
    title: "Infographic: Complexity Cheat Sheet",
    type: "image",
    resourceUrl: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1080&q=80",
    fileSize: "PNG",
    uploadedAt: "2026-01-10T09:00:00",
    previewLabel: "Preview",
  },
  {
    id: "material-cs101-4",
    topicId: "topic-cs101-2",
    title: "Lab Guide: Debugging Starter Code",
    type: "file",
    resourceUrl: "/materials/cs101-debugging.docx",
    fileSize: "540 KB",
    uploadedAt: "2026-01-12T09:00:00",
    previewLabel: "DOCX",
  },
  {
    id: "material-cs101-5",
    topicId: "topic-cs101-2",
    title: "Video: Reading Hidden Test Failures",
    type: "video",
    resourceUrl: "https://video.example.com/hidden-tests",
    fileSize: "12:45",
    uploadedAt: "2026-01-13T09:00:00",
    previewLabel: "MP4",
  },
  {
    id: "material-cs102-1",
    topicId: "topic-cs102-1",
    title: "Slides: Binary Search Tree Operations",
    type: "file",
    resourceUrl: "/materials/cs102-bst.pdf",
    fileSize: "3.1 MB",
    uploadedAt: "2026-01-15T09:00:00",
    previewLabel: "PDF",
  },
  {
    id: "material-cs102-2",
    topicId: "topic-cs102-1",
    title: "Diagram: Recursive Traversal Order",
    type: "image",
    resourceUrl: "https://images.unsplash.com/photo-1516116216624-53e697fedbea?auto=format&fit=crop&w=1080&q=80",
    fileSize: "JPG",
    uploadedAt: "2026-01-16T09:00:00",
    previewLabel: "Preview",
  },
  {
    id: "material-cs102-3",
    topicId: "topic-cs102-2",
    title: "Video: Merge Sort Animation",
    type: "video",
    resourceUrl: "https://video.example.com/merge-sort",
    fileSize: "18:04",
    uploadedAt: "2026-01-17T09:00:00",
    previewLabel: "MP4",
  },
  {
    id: "material-cs102-4",
    topicId: "topic-cs102-2",
    title: "Worksheet: Complexity Comparison",
    type: "file",
    resourceUrl: "/materials/cs102-complexity.xlsx",
    fileSize: "320 KB",
    uploadedAt: "2026-01-18T09:00:00",
    previewLabel: "XLSX",
  },
  {
    id: "material-cs201-1",
    topicId: "topic-cs201-1",
    title: "Slides: useState And Async UI",
    type: "file",
    resourceUrl: "/materials/cs201-state.pdf",
    fileSize: "1.9 MB",
    uploadedAt: "2026-01-20T09:00:00",
    previewLabel: "PDF",
  },
  {
    id: "material-cs201-2",
    topicId: "topic-cs201-1",
    title: "Video: Component Data Flow",
    type: "video",
    resourceUrl: "https://video.example.com/data-flow",
    fileSize: "21:10",
    uploadedAt: "2026-01-21T09:00:00",
    previewLabel: "MP4",
  },
  {
    id: "material-cs202-1",
    topicId: "topic-cs202-1",
    title: "Mobile API Integration Checklist",
    type: "file",
    resourceUrl: "/materials/cs202-api-checklist.pdf",
    fileSize: "900 KB",
    uploadedAt: "2026-01-22T09:00:00",
    previewLabel: "PDF",
  },
  {
    id: "material-cs202-2",
    topicId: "topic-cs202-1",
    title: "Screen Mockup: Error States",
    type: "image",
    resourceUrl: "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=1080&q=80",
    fileSize: "PNG",
    uploadedAt: "2026-01-23T09:00:00",
    previewLabel: "Preview",
  },
]

export const initialSubmissionHistory: SubmissionRecord[] = [
  {
    id: "submission-1",
    assignmentId: "1",
    startedAt: "2026-02-13T20:00:00",
    submittedAt: "2026-02-13T20:10:00",
    finishedAt: "2026-02-13T20:10:00",
    durationSeconds: 600,
    language: "python",
    score: 78,
    passed: 3,
    total: 4,
    status: "reviewed",
    code: codingProblems[0]?.functionSkeleton.python ?? "",
    testResults: [
      { idx: 1, input: "[2,7,11,15], 9", expected: "[0,1]", actual: "[0,1]", passed: true, hidden: false },
      { idx: 2, input: "[3,2,4], 6", expected: "[1,2]", actual: "[1,2]", passed: true, hidden: false },
      { idx: 3, input: "[3,3], 6", expected: "[0,1]", actual: "[0,1]", passed: true, hidden: true },
      { idx: 4, input: "[-1,-2,-3,-4,-5], -8", expected: "[2,4]", actual: "[]", passed: false, hidden: true },
    ],
  },
  {
    id: "submission-2",
    assignmentId: "4",
    startedAt: "2026-02-07T19:28:00",
    submittedAt: "2026-02-07T19:40:00",
    finishedAt: "2026-02-07T19:40:00",
    durationSeconds: 720,
    language: "javascript",
    score: 100,
    passed: 5,
    total: 5,
    status: "reviewed",
    code: codingProblems[1]?.functionSkeleton.javascript ?? "",
    testResults: [
      { idx: 1, input: "121", expected: "true", actual: "true", passed: true, hidden: false },
      { idx: 2, input: "-121", expected: "false", actual: "false", passed: true, hidden: false },
      { idx: 3, input: "10", expected: "false", actual: "false", passed: true, hidden: false },
      { idx: 4, input: "0", expected: "true", actual: "true", passed: true, hidden: true },
      { idx: 5, input: "12321", expected: "true", actual: "true", passed: true, hidden: true },
    ],
  },
  {
    id: "submission-3",
    assignmentId: "8",
    startedAt: "2026-02-04T21:59:00",
    submittedAt: "2026-02-04T22:15:00",
    finishedAt: "2026-02-04T22:15:00",
    durationSeconds: 960,
    language: "cpp",
    score: 88,
    passed: 4,
    total: 5,
    status: "reviewed",
    code: codingProblems[2]?.functionSkeleton.cpp ?? "",
    testResults: [
      { idx: 1, input: "[12, 11, 13, 5, 6, 7]", expected: "[5, 6, 7, 11, 12, 13]", actual: "[5, 6, 7, 11, 12, 13]", passed: true, hidden: false },
      { idx: 2, input: "[38, 27, 43, 3, 9, 82, 10]", expected: "[3, 9, 10, 27, 38, 43, 82]", actual: "[3, 9, 10, 27, 38, 43, 82]", passed: true, hidden: false },
      { idx: 3, input: "[1]", expected: "[1]", actual: "[1]", passed: true, hidden: true },
      { idx: 4, input: "[]", expected: "[]", actual: "[]", passed: true, hidden: true },
      { idx: 5, input: "[5, 2, 3, 1]", expected: "[1, 2, 3, 5]", actual: "[1, 2, 5, 3]", passed: false, hidden: true },
    ],
  },
]

export const baseCodeReviews: CodeReviewFeedback[] = [
  {
    assignmentId: "1",
    strengths: [
      "The function signature matches the expected platform format.",
      "Your control flow stays focused on a single pass, which is the right direction for this problem.",
    ],
    weaknesses: [
      "The current solution still misses one hidden edge case involving negative values.",
      "Variable naming can be clearer around the lookup structure and the current index.",
    ],
    improvements: [
      "Use a hash map to store values you have already seen and check `target - current` first.",
      "Return early as soon as you detect a valid pair to keep the code path compact.",
    ],
  },
  {
    assignmentId: "4",
    strengths: [
      "The negative-number guard is correct and prevents invalid palindrome checks early.",
      "The solution is short, readable, and easy to reason about.",
    ],
    weaknesses: [
      "String conversion is simple but hides the number-manipulation idea the assignment is targeting.",
    ],
    improvements: [
      "Try reversing only half of the number to avoid unnecessary memory allocation.",
      "Add a short comment that explains the early return conditions for `x < 0` and trailing zeroes.",
    ],
  },
  {
    assignmentId: "8",
    strengths: [
      "The recursive split phase is structured correctly and handles the base case cleanly.",
      "You separate the algorithm into smaller steps, which makes the code easier to extend.",
    ],
    weaknesses: [
      "The merge step still has one ordering bug, which shows up on mixed-value hidden tests.",
      "Temporary array handling could be cleaner to avoid duplicated branching.",
    ],
    improvements: [
      "Extract `merge(left, right)` into a helper and keep the recursive function focused on splitting.",
      "Write a quick dry run for `[5,2,3,1]` to verify pointer movement during merge.",
    ],
  },
]

export const initialProblemBank: ProblemBankEntry[] = [
  {
    id: "bank-1",
    title: "Contains Duplicate",
    description: "Detect whether an array contains any repeated element using an efficient lookup structure.",
    difficulty: "Easy",
    topics: ["Array", "Hash Table"],
    estimatedMinutes: 15,
    recommendedForCourseIds: ["1"],
    solvedByStudentIds: [studentProfile.id],
    source: "bank",
  },
  {
    id: "bank-2",
    title: "Valid Anagram",
    description: "Compare two strings and decide whether they are anagrams under frequency constraints.",
    difficulty: "Easy",
    topics: ["String", "Hash Table"],
    estimatedMinutes: 20,
    recommendedForCourseIds: ["1"],
    solvedByStudentIds: [],
    source: "bank",
  },
  {
    id: "bank-3",
    title: "Best Time To Buy And Sell Stock",
    description: "Track the best achievable profit while scanning prices only once.",
    difficulty: "Easy",
    topics: ["Array", "Dynamic Programming"],
    estimatedMinutes: 20,
    recommendedForCourseIds: ["1"],
    solvedByStudentIds: [],
    source: "bank",
  },
  {
    id: "bank-4",
    title: "Validate Binary Search Tree",
    description: "Verify whether a tree satisfies the BST invariant across all descendants.",
    difficulty: "Medium",
    topics: ["Tree", "Depth-First Search"],
    estimatedMinutes: 35,
    recommendedForCourseIds: ["2"],
    solvedByStudentIds: [],
    source: "bank",
  },
  {
    id: "bank-5",
    title: "Kth Smallest Element In BST",
    description: "Traverse a binary search tree and locate the kth smallest node efficiently.",
    difficulty: "Medium",
    topics: ["Tree", "Stack", "Inorder Traversal"],
    estimatedMinutes: 40,
    recommendedForCourseIds: ["2"],
    solvedByStudentIds: [studentProfile.id],
    source: "bank",
  },
  {
    id: "bank-6",
    title: "Sort Colors",
    description: "Rearrange an array in-place using pointer-based partitioning.",
    difficulty: "Medium",
    topics: ["Array", "Two Pointers", "Sorting"],
    estimatedMinutes: 30,
    recommendedForCourseIds: ["2"],
    solvedByStudentIds: [],
    source: "bank",
  },
  {
    id: "bank-7",
    title: "Responsive Task Board",
    description: "Build a responsive kanban board with drag state, filters, and optimistic UI.",
    difficulty: "Hard",
    topics: ["React", "UI State", "Async Patterns"],
    estimatedMinutes: 75,
    recommendedForCourseIds: ["5"],
    solvedByStudentIds: [],
    source: "lecturer",
  },
]

export const studentPerformance: StudentPerformanceRecord[] = [
  {
    id: "student-001",
    name: "Nguyen Xuan Hien",
    email: "student@bklearninghub.edu",
    courseId: "1",
    averageScore: 89,
    solvedProblems: 12,
    lastSubmissionAt: "2026-02-13T20:10:00",
    status: "excelling",
    assignmentScores: [
      { assignmentId: "1", assignmentTitle: "Two Sum", score: 78, submittedAt: "2026-02-13T20:10:00" },
      { assignmentId: "4", assignmentTitle: "Palindrome Number", score: 100, submittedAt: "2026-02-07T19:40:00" },
    ],
  },
  {
    id: "student-002",
    name: "Le Thi Minh Chau",
    email: "chau@bklearninghub.edu",
    courseId: "1",
    averageScore: 74,
    solvedProblems: 8,
    lastSubmissionAt: "2026-02-12T21:20:00",
    status: "stable",
    assignmentScores: [
      { assignmentId: "1", assignmentTitle: "Two Sum", score: 72, submittedAt: "2026-02-12T21:20:00" },
      { assignmentId: "4", assignmentTitle: "Palindrome Number", score: 76, submittedAt: "2026-02-06T18:00:00" },
    ],
  },
  {
    id: "student-003",
    name: "Pham Duc Long",
    email: "long@bklearninghub.edu",
    courseId: "1",
    averageScore: 61,
    solvedProblems: 5,
    lastSubmissionAt: "2026-02-11T22:15:00",
    status: "at-risk",
    assignmentScores: [
      { assignmentId: "1", assignmentTitle: "Two Sum", score: 58, submittedAt: "2026-02-11T22:15:00" },
      { assignmentId: "4", assignmentTitle: "Palindrome Number", score: 64, submittedAt: "2026-02-05T17:30:00" },
    ],
  },
  {
    id: "student-004",
    name: "Tran Hoang Vy",
    email: "vy@bklearninghub.edu",
    courseId: "2",
    averageScore: 84,
    solvedProblems: 10,
    lastSubmissionAt: "2026-02-10T20:30:00",
    status: "stable",
    assignmentScores: [
      { assignmentId: "2", assignmentTitle: "Binary Search Tree", score: 82, submittedAt: "2026-02-10T20:30:00" },
      { assignmentId: "8", assignmentTitle: "Merge Sort", score: 86, submittedAt: "2026-02-04T21:00:00" },
    ],
  },
]

export const lecturerManagedCourses = courses.filter((course) =>
  ["1", "2", "5"].includes(course.id)
)

export const fallbackTopicAssignments = assignments.filter((assignment) =>
  lecturerManagedCourses.some((course) => course.id === assignment.courseId)
)
