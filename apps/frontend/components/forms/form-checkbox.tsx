"use client"

import type * as React from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { AlertCircle } from "lucide-react"

export interface FormCheckboxProps {
  label?: string
  description?: string
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
  error?: string
  disabled?: boolean
  isRequired?: boolean
  id?: string
  className?: string
}

export const FormCheckbox: React.FC<FormCheckboxProps> = ({
  label,
  description,
  checked,
  onCheckedChange,
  error,
  disabled = false,
  isRequired = false,
  id,
  className,
}) => {
  const checkboxId = id || `checkbox-${label?.toLowerCase().replace(/\s+/g, "-")}`

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-start space-x-3">
        <Checkbox
          id={checkboxId}
          checked={checked}
          onCheckedChange={onCheckedChange}
          disabled={disabled}
          aria-invalid={!!error}
          aria-required={isRequired}
          className={cn(error && "border-destructive")}
        />
        <div className="flex-1 space-y-1">
          {label && (
            <Label
              htmlFor={checkboxId}
              className={cn(
                "text-sm font-medium leading-none cursor-pointer",
                disabled && "cursor-not-allowed opacity-70",
              )}
            >
              {label}
              {isRequired && (
                <span className="text-destructive ml-1" aria-label="required">
                  *
                </span>
              )}
            </Label>
          )}
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      </div>
      {error && (
        <p className="text-sm text-destructive flex items-center gap-1 pl-7">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
    </div>
  )
}
