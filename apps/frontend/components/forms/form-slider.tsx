"use client"

import type * as React from "react"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { AlertCircle } from "lucide-react"

export interface FormSliderProps {
  label?: string
  value?: number[]
  onChange?: (value: number[]) => void
  min?: number
  max?: number
  step?: number
  error?: string
  helperText?: string
  isRequired?: boolean
  disabled?: boolean
  showValue?: boolean
  formatValue?: (value: number) => string
  id?: string
  className?: string
}

export const FormSlider: React.FC<FormSliderProps> = ({
  label,
  value = [0],
  onChange,
  min = 0,
  max = 100,
  step = 1,
  error,
  helperText,
  isRequired = false,
  disabled = false,
  showValue = true,
  formatValue = (val) => val.toString(),
  id,
  className,
}) => {
  const sliderId = id || `slider-${label?.toLowerCase().replace(/\s+/g, "-")}`

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center justify-between">
        {label && (
          <Label htmlFor={sliderId} className="text-sm font-medium">
            {label}
            {isRequired && (
              <span className="text-destructive ml-1" aria-label="required">
                *
              </span>
            )}
          </Label>
        )}
        {showValue && (
          <span className="text-sm font-medium text-primary">
            {value.length === 2 ? `${formatValue(value[0])} - ${formatValue(value[1])}` : formatValue(value[0])}
          </span>
        )}
      </div>
      <Slider
        id={sliderId}
        value={value}
        onValueChange={onChange}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        aria-invalid={!!error}
        aria-required={isRequired}
        className={cn(error && "border-destructive")}
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{formatValue(min)}</span>
        <span>{formatValue(max)}</span>
      </div>
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
