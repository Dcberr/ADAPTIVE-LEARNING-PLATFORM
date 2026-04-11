import LmsShell from "@/components/lms/LmsShell"

export default function Layout({ children }: { children: React.ReactNode }) {
  return <LmsShell role="student">{children}</LmsShell>
}
