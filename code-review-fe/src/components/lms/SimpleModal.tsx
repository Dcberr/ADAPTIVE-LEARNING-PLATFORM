"use client"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

export default function SimpleModal({
  open,
  title,
  description,
  onClose,
  children,
}: {
  open: boolean
  title: string
  description?: string
  onClose: () => void
  children: React.ReactNode
}) {
  return (
    <Dialog open={open} onOpenChange={(nextOpen) => (!nextOpen ? onClose() : undefined)}>
      <DialogContent className="grid max-h-[90vh] grid-rows-[auto_minmax(0,1fr)] overflow-hidden p-0 sm:max-w-3xl">
        <DialogHeader className="shrink-0 border-b border-slate-100 bg-white px-6 py-5 pr-14">
          <DialogTitle>{title}</DialogTitle>
          {description ? <DialogDescription>{description}</DialogDescription> : null}
        </DialogHeader>
        <div className="min-h-0 overflow-y-auto px-6 py-6">{children}</div>
      </DialogContent>
    </Dialog>
  )
}
