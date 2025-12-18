"use client"

import type * as React from "react"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { cn } from "@/lib/utils"
import { AlertCircle } from "lucide-react"

export interface RadioOption {
  label: string
  value: string
  description?: string
  disabled?: boolean
}

export interface FormRadioProps {
  label?: string
  options: RadioOption[]
  value?: string
  onChange?: (value: string) => void
  error?: string
  helperText?: string
  isRequired?: boolean
  disabled?: boolean
  orientation?: "vertical" | "horizontal"
  id?: string
}

export const FormRadio: React.FC<FormRadioProps> = ({
  label,
  options,
  value,
  onChange,
  error,
  helperText,
  isRequired = false,
  disabled = false,
  orientation = "vertical",
  id,
}) => {
  const radioId = id || `radio-${label?.toLowerCase().replace(/\s+/g, "-")}`

  return (
    <div className="space-y-3">
      {label && (
        <Label className="text-sm font-medium">
          {label}
          {isRequired && (
            <span className="text-destructive ml-1" aria-label="required">
              *
            </span>
          )}
        </Label>
      )}
      <RadioGroup
        id={radioId}
        value={value}
        onValueChange={onChange}
        disabled={disabled}
        className={cn("gap-3", orientation === "horizontal" && "flex flex-wrap")}
        aria-invalid={!!error}
        aria-required={isRequired}
      >
        {options.map((option) => (
          <div key={option.value} className="flex items-start space-x-3">
            <RadioGroupItem
              value={option.value}
              id={`${radioId}-${option.value}`}
              disabled={option.disabled || disabled}
              className={cn(error && "border-destructive")}
            />
            <div className="flex-1 space-y-1">
              <Label
                htmlFor={`${radioId}-${option.value}`}
                className={cn(
                  "text-sm font-medium leading-none cursor-pointer",
                  (option.disabled || disabled) && "cursor-not-allowed opacity-70",
                )}
              >
                {option.label}
              </Label>
              {option.description && <p className="text-sm text-muted-foreground">{option.description}</p>}
            </div>
          </div>
        ))}
      </RadioGroup>
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
