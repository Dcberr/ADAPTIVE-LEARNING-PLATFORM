import AuthGuard from "@/components/lms/auth/AuthGuard"
import LmsShell from "@/components/lms/LmsShell"

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard requiredRole="student">
      <LmsShell role="student">{children}</LmsShell>
    </AuthGuard>
  )
}
