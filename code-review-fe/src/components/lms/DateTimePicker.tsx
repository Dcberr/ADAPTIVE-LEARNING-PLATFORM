"use client"

import { useState } from "react"
import { format } from "date-fns"
import { CalendarIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"

function parseDateTimeValue(value: string): Date | null {
  if (!value) return null
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function pad(value: number) {
  return value.toString().padStart(2, "0")
}

function toDateTimeString(date: Date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(
    date.getHours()
  )}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

function withTime(baseDate: Date, time: string) {
  const [hours, minutes, seconds] = time.split(":").map((segment) => Number(segment))
  const next = new Date(baseDate)
  next.setHours(
    Number.isFinite(hours) ? hours : 0,
    Number.isFinite(minutes) ? minutes : 0,
    Number.isFinite(seconds) ? seconds : 0,
    0
  )
  return next
}

export default function DateTimePicker({
  value,
  placeholder,
  onChange,
}: {
  value: string
  placeholder: string
  onChange: (value: string) => void
}) {
  const [open, setOpen] = useState(false)
  const selectedDate = parseDateTimeValue(value)
  const selectedTime = selectedDate
    ? `${pad(selectedDate.getHours())}:${pad(selectedDate.getMinutes())}:${pad(selectedDate.getSeconds())}`
    : "09:00:00"

  return (
    <div className="flex items-end gap-3">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            type="button"
            variant="outline"
            className={cn(
              "h-11 flex-1 justify-between rounded-xl border-slate-200 px-3 font-normal",
              !selectedDate ? "text-slate-400" : "text-slate-800"
            )}
          >
            {selectedDate ? format(selectedDate, "PPP") : placeholder}
            <CalendarIcon className="size-4 text-slate-500" />
          </Button>
        </PopoverTrigger>
        <PopoverContent align="start" className="w-auto overflow-hidden rounded-2xl p-0">
          <Calendar
            mode="single"
            selected={selectedDate ?? undefined}
            defaultMonth={selectedDate ?? undefined}
            onSelect={(date) => {
              if (!date) {
                return
              }

              onChange(toDateTimeString(withTime(date, selectedTime)))
              setOpen(false)
            }}
          />
        </PopoverContent>
      </Popover>
      <div className="w-32">
        <Input
          type="time"
          step="1"
          value={selectedTime}
          onChange={(event) => {
            const baseDate = selectedDate ?? new Date()
            onChange(toDateTimeString(withTime(baseDate, event.target.value)))
          }}
          className="h-11 rounded-xl border-slate-200 appearance-none bg-background [&::-webkit-calendar-picker-indicator]:hidden [&::-webkit-calendar-picker-indicator]:appearance-none"
        />
      </div>
    </div>
  )
}
