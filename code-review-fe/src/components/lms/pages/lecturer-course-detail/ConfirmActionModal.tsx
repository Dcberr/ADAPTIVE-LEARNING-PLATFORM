"use client"

import { AlertTriangle } from "lucide-react"

import SimpleModal from "@/components/lms/SimpleModal"
import { Button } from "@/components/ui/button"

export default function ConfirmActionModal({
  open,
  title,
  description,
  confirmLabel,
  isSubmitting,
  onClose,
  onConfirm,
}: {
  open: boolean
  title: string
  description: string
  confirmLabel: string
  isSubmitting: boolean
  onClose: () => void
  onConfirm: () => void
}) {
  return (
    <SimpleModal open={open} title={title} description="Hành động này không thể hoàn tác." onClose={onClose}>
      <div className="space-y-5">
        <div className="flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-4 text-sm text-rose-900">
          <AlertTriangle className="mt-0.5 size-5 shrink-0" />
          <p>{description}</p>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose} disabled={isSubmitting}>
            Hủy
          </Button>
          <Button
            className="bg-rose-600 text-white hover:bg-rose-700"
            onClick={onConfirm}
            disabled={isSubmitting}
          >
            {isSubmitting ? "Đang xử lý..." : confirmLabel}
          </Button>
        </div>
      </div>
    </SimpleModal>
  )
}
