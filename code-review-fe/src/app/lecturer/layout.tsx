import AuthGuard from "@/components/lms/auth/AuthGuard"
import LmsShell from "@/components/lms/LmsShell"

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard requiredRole="lecturer">
      <LmsShell role="lecturer">{children}</LmsShell>
    </AuthGuard>
  )
}
