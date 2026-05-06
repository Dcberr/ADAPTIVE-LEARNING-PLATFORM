"use client"

import { useMemo, useState } from "react"
import { Check, ChevronsUpDown, X } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import {
  FIXED_TAG_OPTIONS,
  getFixedTagOption,
  normalizeFixedTagSlugs,
} from "@/components/lms/tagOptions"

function getTagBadgeClassName(tag: string) {
  const palette = [
    "border-sky-200 bg-sky-50 text-sky-700 hover:bg-sky-50",
    "border-cyan-200 bg-cyan-50 text-cyan-700 hover:bg-cyan-50",
    "border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-50",
    "border-violet-200 bg-violet-50 text-violet-700 hover:bg-violet-50",
    "border-teal-200 bg-teal-50 text-teal-700 hover:bg-teal-50",
    "border-fuchsia-200 bg-fuchsia-50 text-fuchsia-700 hover:bg-fuchsia-50",
  ]
  const index = Array.from(tag).reduce((sum, char) => sum + char.charCodeAt(0), 0) % palette.length

  return palette[index]
}

export default function MultiTagCombobox({
  value,
  onChange,
  placeholder = "Chọn tag",
}: {
  value: string[]
  onChange: (value: string[]) => void
  placeholder?: string
}) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const normalizedValue = useMemo(() => normalizeFixedTagSlugs(value), [value])

  return (
    <div className="space-y-2">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            type="button"
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="h-auto min-h-11 w-full justify-between rounded-xl px-3 py-2"
          >
            <span
              className={cn(
                "truncate text-left text-sm",
                normalizedValue.length === 0 ? "text-slate-400" : "text-slate-700"
              )}
            >
              {normalizedValue.length === 0
                ? placeholder
                : `${normalizedValue.length} tag đã chọn`}
            </span>
            <ChevronsUpDown className="ml-2 size-4 shrink-0 text-slate-400" />
          </Button>
        </PopoverTrigger>
        <PopoverContent align="start" className="pointer-events-auto w-[var(--radix-popover-trigger-width)] p-0">
          <Command shouldFilter>
            <CommandInput
              value={query}
              onValueChange={setQuery}
              placeholder="Tìm theo tên hoặc slug"
            />
            <CommandList onWheel={(e)=>{e.stopPropagation()}}>
              <CommandEmpty>Không tìm thấy tag phù hợp.</CommandEmpty>
              <CommandGroup>
                {FIXED_TAG_OPTIONS.map((option) => {
                  const isSelected = normalizedValue.includes(option.slug)

                  return (
                    <CommandItem
                      key={option.slug}
                      value={`${option.label} ${option.slug}`}
                      onSelect={() => {
                        onChange(
                          isSelected
                            ? normalizedValue.filter((item) => item !== option.slug)
                            : normalizeFixedTagSlugs([...normalizedValue, option.slug])
                        )
                      }}
                    >
                      <Check
                        className={cn(
                          "size-4 text-[#030391]",
                          isSelected ? "opacity-100" : "opacity-0"
                        )}
                      />
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-900">{option.label}</p>
                        <p className="text-xs text-slate-500">{option.slug}</p>
                      </div>
                    </CommandItem>
                  )
                })}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {normalizedValue.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {normalizedValue.map((slug) => {
            const option = getFixedTagOption(slug)
            const label = option?.label ?? slug

            return (
              <Badge
                key={slug}
                variant="outline"
                className={cn("gap-1 rounded-full pr-1", getTagBadgeClassName(slug))}
              >
                <span>{label}</span>
                <button
                  type="button"
                  className="rounded-full p-0.5 hover:bg-black/10"
                  onClick={() => onChange(normalizedValue.filter((item) => item !== slug))}
                >
                  <X className="size-3" />
                </button>
              </Badge>
            )
          })}
        </div>
      ) : null}
    </div>
  )
}
