"use client"

import type * as React from "react"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { AlertCircle } from "lucide-react"

export interface FormSwitchProps {
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

export const FormSwitch: React.FC<FormSwitchProps> = ({
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
  const switchId = id || `switch-${label?.toLowerCase().replace(/\s+/g, "-")}`

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between space-x-4">
        <div className="flex-1 space-y-1">
          {label && (
            <Label
              htmlFor={switchId}
              className={cn("text-sm font-medium cursor-pointer", disabled && "cursor-not-allowed opacity-70")}
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
        <Switch
          id={switchId}
          checked={checked}
          onCheckedChange={onCheckedChange}
          disabled={disabled}
          aria-invalid={!!error}
          aria-required={isRequired}
        />
      </div>
      {error && (
        <p className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
    </div>
  )
}
