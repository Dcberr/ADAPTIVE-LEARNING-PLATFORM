import Link from "next/link"

import { assignments } from "@/data/lms/mockData"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { formatDate } from "@/components/lms/date"

function AssignmentList({ status }: { status?: string }) {
  const list = status ? assignments.filter((item) => item.status === status) : assignments

  return (
    <div className="space-y-3">
      {list.map((item) => (
        <Link key={item.id} href={`/student/assignments/${item.id}`} className="block">
          <Card className="transition hover:bg-slate-50">
            <CardContent className="flex items-center justify-between gap-3 py-5">
              <div>
                <Badge className={`${item.courseColor} text-white`}>{item.courseName}</Badge>
                <p className="mt-2 font-medium">{item.title}</p>
                <p className="mt-1 text-xs text-slate-500">Hạn nộp: {formatDate(item.dueDate)}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {item.points} điểm • {item.difficulty ?? "Mixed"} • {item.type ?? "code"}
                </p>
              </div>
              <Badge variant="outline">{item.status}</Badge>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  )
}

export default function AssignmentsPage() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Bài tập</CardTitle>
        </CardHeader>
      </Card>
      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">Tất cả</TabsTrigger>
          <TabsTrigger value="pending">Chờ nộp</TabsTrigger>
          <TabsTrigger value="submitted">Đã nộp</TabsTrigger>
          <TabsTrigger value="graded">Đã chấm</TabsTrigger>
        </TabsList>
        <TabsContent value="all">
          <AssignmentList />
        </TabsContent>
        <TabsContent value="pending">
          <AssignmentList status="pending" />
        </TabsContent>
        <TabsContent value="submitted">
          <AssignmentList status="submitted" />
        </TabsContent>
        <TabsContent value="graded">
          <AssignmentList status="graded" />
        </TabsContent>
      </Tabs>
    </div>
  )
}
