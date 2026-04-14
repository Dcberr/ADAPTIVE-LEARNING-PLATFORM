"use client"

import { memo } from "react"
import { LoaderCircle, Trash2, UserRound } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { ClassStudent } from "@/store/redux/api/lmsApi"

function StudentsMonitoringTabComponent({
  students,
  isLoading,
  isRemovingStudent,
  removingStudentCode,
  onRemoveStudent,
}: {
  students: ClassStudent[]
  isLoading: boolean
  isRemovingStudent: boolean
  removingStudentCode: string | null
  onRemoveStudent: (userCode: string) => Promise<void>
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-[#030391]">Danh sách sinh viên</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
            Đang tải danh sách sinh viên...
          </div>
        ) : null}

        {!isLoading && students.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center">
            <p className="font-medium text-[#030391]">Lớp này chưa có sinh viên nào.</p>
          </div>
        ) : null}

        {!isLoading
          ? students.map((student) => {
              const isRemovingCurrentStudent =
                isRemovingStudent && removingStudentCode === student.userCode
              const fallbackLabel = student.name
                .split(" ")
                .filter(Boolean)
                .slice(0, 2)
                .map((item) => item[0]?.toUpperCase() ?? "")
                .join("")

              return (
                <div key={student.id} className="rounded-2xl border border-slate-200 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="flex min-w-0 items-center gap-3">
                      {student.picture ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={student.picture}
                          alt={student.name}
                          className="size-12 rounded-full border border-slate-200 object-cover"
                        />
                      ) : (
                        <div className="flex size-12 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-600">
                          {fallbackLabel || <UserRound className="size-5" />}
                        </div>
                      )}
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-slate-900">{student.name}</p>
                        <p className="mt-1 truncate text-sm text-slate-500">{student.email}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          <Badge variant="outline">{student.userCode}</Badge>
                          <Badge className="bg-sky-100 text-sky-700 hover:bg-sky-100">
                            {student.role}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <Button
                      type="button"
                      variant="outline"
                      className="border-rose-200 text-rose-600 hover:bg-rose-50 hover:text-rose-700"
                      disabled={isRemovingStudent}
                      onClick={() => void onRemoveStudent(student.userCode)}
                    >
                      {isRemovingCurrentStudent ? (
                        <>
                          <LoaderCircle className="size-4 animate-spin" />
                          Đang xóa...
                        </>
                      ) : (
                        <>
                          <Trash2 className="size-4" />
                          Xóa khỏi lớp
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )
            })
          : null}
      </CardContent>
    </Card>
  )
}

const StudentsMonitoringTab = memo(StudentsMonitoringTabComponent)

export default StudentsMonitoringTab
