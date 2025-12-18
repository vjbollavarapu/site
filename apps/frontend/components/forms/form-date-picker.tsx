"use client"

import * as React from "react"
import { format } from "date-fns"
import { CalendarIcon, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import type { DateRange } from "react-day-picker"

export interface FormDatePickerProps {
  label?: string
  placeholder?: string
  value?: Date | DateRange
  onChange?: (date: Date | DateRange | undefined) => void
  error?: string
  helperText?: string
  isRequired?: boolean
  disabled?: boolean
  isRange?: boolean
  id?: string
}

export const FormDatePicker: React.FC<FormDatePickerProps> = ({
  label,
  placeholder = "Pick a date",
  value,
  onChange,
  error,
  helperText,
  isRequired = false,
  disabled = false,
  isRange = false,
  id,
}) => {
  const [open, setOpen] = React.useState(false)
  const datePickerId = id || `datepicker-${label?.toLowerCase().replace(/\s+/g, "-")}`

  const getDisplayText = () => {
    if (!value) return placeholder

    if (isRange && value && typeof value === "object" && "from" in value) {
      const range = value as DateRange
      if (range.from) {
        if (range.to) {
          return `${format(range.from, "LLL dd, y")} - ${format(range.to, "LLL dd, y")}`
        }
        return format(range.from, "LLL dd, y")
      }
      return placeholder
    }

    if (value instanceof Date) {
      return format(value, "PPP")
    }

    return placeholder
  }

  return (
    <div className="space-y-2">
      {label && (
        <Label htmlFor={datePickerId} className="text-sm font-medium">
          {label}
          {isRequired && (
            <span className="text-destructive ml-1" aria-label="required">
              *
            </span>
          )}
        </Label>
      )}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            id={datePickerId}
            variant="outline"
            disabled={disabled}
            className={cn(
              "w-full justify-start text-left font-normal",
              !value && "text-muted-foreground",
              error && "border-destructive",
            )}
            aria-invalid={!!error}
            aria-required={isRequired}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {getDisplayText()}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          {isRange ? (
            <Calendar
              mode="range"
              selected={value as DateRange}
              onSelect={(range) => {
                onChange?.(range as DateRange)
                if (range?.from && range?.to) {
                  setOpen(false)
                }
              }}
              disabled={disabled}
              initialFocus
            />
          ) : (
            <Calendar
              mode="single"
              selected={value as Date}
              onSelect={(date) => {
                onChange?.(date)
                setOpen(false)
              }}
              disabled={disabled}
              initialFocus
            />
          )}
        </PopoverContent>
      </Popover>
      {error && (
        <p className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
      {!error && helperText && <p className="text-sm text-muted-foreground">{helperText}</p>}
    </div>
  )
}
