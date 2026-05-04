import type { UserRole } from "@/data/lms/extendedMockData"
import ProblemBankManagementSection from "@/components/lms/pages/problem-bank/ProblemBankManagementSection"

export default function ProblemBankPage({
  role = "lecturer",
  canManage = role === "lecturer",
}: {
  role?: UserRole
  canManage?: boolean
}) {
  return (
    <div className="space-y-6">
      <ProblemBankManagementSection role={role} canManage={canManage} />
    </div>
  )
}
