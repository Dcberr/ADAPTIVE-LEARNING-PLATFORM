import { grades } from "@/data/lms/mockData"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

export default function GradesPage() {
  const average = Math.round(grades.reduce((sum, item) => sum + item.grade, 0) / grades.length)

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Tổng quan điểm số</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{average}%</p>
          <Progress className="mt-3" value={average} />
        </CardContent>
      </Card>

      <div className="space-y-3">
        {grades.map((item) => (
          <Card key={item.courseId}>
            <CardContent className="py-5">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Badge className={`${item.courseColor} text-white`}>{item.courseName}</Badge>
                </div>
                <p className="font-semibold">{item.grade}%</p>
              </div>
              <Progress value={item.grade} />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
