"use client"

import Link from "next/link"
import { BookOpen, Settings, User } from "lucide-react"

import ExternalAvatar from "@/components/lms/ExternalAvatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { useAppSelector } from "@/store/redux/hooks"

export default function ProfilePage() {
  const { user, selectedRole } = useAppSelector((state) => state.auth)
  const resolvedRole = selectedRole ?? "student"
  const roleLabel = resolvedRole === "lecturer" ? "Giảng viên" : "Sinh viên"
  const initials =
    user?.name
      ?.split(" ")
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase() ?? "BK"
  const academicIdLabel = resolvedRole === "lecturer" ? "MSCB" : "MSSV"
  const academicIdValue = user?.userCode ?? ""

  return (
    <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Hồ sơ {roleLabel.toLowerCase()}</CardTitle>
        </CardHeader>
        <CardContent>
          <ExternalAvatar
            src={user?.picture}
            alt={user?.name ?? "Avatar"}
            className="mb-4 size-24 rounded-full object-cover shadow-sm"
            fallback={
              <div className="mb-4 flex size-24 items-center justify-center rounded-3xl bg-[#030391] text-2xl font-bold text-white">
                {initials}
              </div>
            }
          />
          <p className="font-semibold">{user?.name ?? "Chưa có thông tin"}</p>
          <p className="text-sm text-slate-500">{user?.email ?? "Chưa có email"}</p>
          <p className="mt-2 text-sm font-medium text-[#030391]">
            {academicIdLabel}: {academicIdValue || "Chưa có mã"}
          </p>
          <Badge className="mt-3">{roleLabel}</Badge>
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
                  <Input id="fullName" defaultValue={user?.name ?? ""} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" defaultValue={user?.email ?? ""} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="bio">Giới thiệu</Label>
                <Textarea id="bio" defaultValue="Sinh viên ngành Khoa học Máy tính, quan tâm AI và hệ thống phân tán." />
              </div>
              <Button className="rounded-2xl bg-[#030391] text-white hover:bg-[#02026f]">
                Lưu thay đổi
              </Button>
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
                  <Label htmlFor="studentId">{academicIdLabel}</Label>
                  <Input id="studentId" value={academicIdValue} readOnly />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">{roleLabel}</Label>
                  <Input id="role" value={roleLabel} readOnly />
                </div>
              </div>
              <Button
                asChild
                className="rounded-2xl bg-[#1488D8] text-white hover:bg-[#0f76bd]"
              >
                <Link href={resolvedRole === "student" ? "/student/dashboard" : "/lecturer/dashboard"}>
                  Quay lại trang chính
                </Link>
              </Button>
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
                Thông báo email
                <input type="checkbox" defaultChecked />
              </label>
              <label className="flex items-center justify-between rounded-md border p-3">
                Nhắc hạn nộp bài
                <input type="checkbox" defaultChecked />
              </label>
              <Button className="rounded-2xl bg-[#030391] text-white hover:bg-[#02026f]">
                Lưu cấu hình
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
