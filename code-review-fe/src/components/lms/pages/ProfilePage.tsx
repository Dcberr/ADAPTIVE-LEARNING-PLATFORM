import { BookOpen, Settings, User } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"

export default function ProfilePage() {
  return (
    <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Hồ sơ sinh viên</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex size-20 items-center justify-center rounded-full bg-[#030391] text-xl font-bold text-white">
            NH
          </div>
          <p className="font-semibold">Nguyễn Xuân Hiển</p>
          <p className="text-sm text-slate-500">Computer Science</p>
          <Badge className="mt-3">K20</Badge>
        </CardContent>
      </Card>

      <Tabs defaultValue="personal">
        <TabsList>
          <TabsTrigger value="personal">
            <User className="size-4" /> Cá nhân
          </TabsTrigger>
          <TabsTrigger value="academic">
            <BookOpen className="size-4" /> Học tập
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="size-4" /> Cài đặt
          </TabsTrigger>
        </TabsList>

        <TabsContent value="personal">
          <Card>
            <CardHeader>
              <CardTitle>Thông tin cá nhân</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="fullName">Họ tên</Label>
                  <Input id="fullName" defaultValue="Nguyễn Xuân Hiển" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" defaultValue="hien.nguyen@hcmut.edu.vn" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="bio">Giới thiệu</Label>
                <Textarea id="bio" defaultValue="Sinh viên ngành Khoa học Máy tính, quan tâm AI và hệ thống phân tán." />
              </div>
              <Button>Lưu thay đổi</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="academic">
          <Card>
            <CardHeader>
              <CardTitle>Thông tin học tập</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="studentId">MSSV</Label>
                  <Input id="studentId" defaultValue="2012345" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="major">Chuyên ngành</Label>
                  <Input id="major" defaultValue="Computer Science" />
                </div>
              </div>
              <Button>Update</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Tùy chọn</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <label className="flex items-center justify-between rounded-md border p-3">
                Email notifications
                <input type="checkbox" defaultChecked />
              </label>
              <label className="flex items-center justify-between rounded-md border p-3">
                Assignment reminders
                <input type="checkbox" defaultChecked />
              </label>
              <Button>Lưu cấu hình</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
