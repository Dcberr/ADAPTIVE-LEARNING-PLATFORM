import { calendarEvents } from "@/data/lms/mockData"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function CalendarPage() {
  const sorted = [...calendarEvents].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  )

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Lịch học và sự kiện</CardTitle>
        </CardHeader>
      </Card>
      {sorted.map((event) => (
        <Card key={event.id}>
          <CardContent className="flex items-center justify-between gap-4 py-5">
            <div>
              <p className="font-medium">{event.title}</p>
              <p className="text-sm text-slate-500">
                {new Date(event.date).toLocaleDateString("vi-VN")} - {event.time}
              </p>
            </div>
            <Badge variant="outline">{event.type}</Badge>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
