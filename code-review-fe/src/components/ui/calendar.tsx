"use client"

import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { DayPicker } from "react-day-picker"

import { buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: React.ComponentProps<typeof DayPicker>) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      navLayout="around"
      className={cn("p-3", className)}
      classNames={{
        months: "flex flex-col sm:flex-row gap-4",
        month: "space-y-4 relative",
        caption: "relative flex items-center justify-center",
        caption_label: "text-sm font-medium",
        dropdowns: "flex items-center gap-2",
        dropdown_root:
          "relative inline-flex items-center rounded-md border border-slate-200 bg-white px-2 py-1 text-sm font-medium text-slate-800 shadow-xs",
        dropdown:
          "absolute inset-0 cursor-pointer opacity-0",
        nav: "absolute inset-x-0 top-0 flex items-center justify-between",
        button_previous: cn(
          buttonVariants({ variant: "outline", size: "icon-sm" }),
          "absolute left-0 top-0 h-7 w-7 rounded-md border-slate-200 bg-transparent p-0 opacity-80 hover:opacity-100"
        ),
        button_next: cn(
          buttonVariants({ variant: "outline", size: "icon-sm" }),
          "absolute right-0 top-0 h-7 w-7 rounded-md border-slate-200 bg-transparent p-0 opacity-80 hover:opacity-100"
        ),
        month_caption: "flex h-10 items-center justify-center px-10 text-sm font-medium",
        month_grid: "border-collapse",
        weekdays: "flex",
        weekday: "w-9 text-[0.8rem] font-normal text-slate-500",
        week: "mt-2 flex w-full",
        day: "relative h-9 w-9 p-0 text-center text-sm focus-within:relative focus-within:z-20",
        day_button: cn(
          buttonVariants({ variant: "ghost" }),
          "h-9 w-9 p-0 font-normal aria-selected:opacity-100"
        ),
        selected:
          "bg-[#030391] text-white hover:bg-[#030391] hover:text-white focus:bg-[#030391] focus:text-white",
        today:
          "bg-slate-100 text-slate-900 [&.rdp-selected]:bg-[#030391] [&.rdp-selected]:text-white [&.rdp-selected_.rdp-day_button]:border-[#030391]",
        outside: "text-slate-400 opacity-70",
        disabled: "text-slate-300 opacity-50",
        hidden: "invisible",
        ...classNames,
      }}
      components={{
        Chevron: ({ orientation, className, ...iconProps }) =>
          orientation === "left" ? (
            <ChevronLeft className={cn("h-4 w-4", className)} {...iconProps} />
          ) : (
            <ChevronRight className={cn("h-4 w-4", className)} {...iconProps} />
          ),
      }}
      {...props}
    />
  )
}

export { Calendar }
