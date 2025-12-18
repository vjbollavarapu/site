"use client"

import * as React from "react"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { AlertCircle, Loader2 } from "lucide-react"

export interface FormTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  helperText?: string
  isRequired?: boolean
  isLoading?: boolean
  showCharCount?: boolean
  maxLength?: number
}

export const FormTextarea = React.forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  (
    {
      label,
      error,
      helperText,
      isRequired = false,
      isLoading = false,
      showCharCount = false,
      maxLength,
      disabled,
      className,
      id,
      value,
      ...props
    },
    ref,
  ) => {
    const textareaId = id || `textarea-${label?.toLowerCase().replace(/\s+/g, "-")}`
    const charCount = value ? String(value).length : 0

    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          {label && (
            <Label htmlFor={textareaId} className="text-sm font-medium">
              {label}
              {isRequired && (
                <span className="text-destructive ml-1" aria-label="required">
                  *
                </span>
              )}
            </Label>
          )}
          {showCharCount && maxLength && (
            <span className="text-xs text-muted-foreground">
              {charCount}/{maxLength}
            </span>
          )}
        </div>
        <div className="relative">
          <Textarea
            ref={ref}
            id={textareaId}
            disabled={disabled || isLoading}
            maxLength={maxLength}
            value={value}
            className={cn(error && "border-destructive focus-visible:ring-destructive", className)}
            aria-invalid={!!error}
            aria-describedby={error ? `${textareaId}-error` : helperText ? `${textareaId}-helper` : undefined}
            aria-required={isRequired}
            {...props}
          />
          {isLoading && (
            <div className="absolute right-3 top-3">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          )}
        </div>
        {error && (
          <p id={`${textareaId}-error`} className="text-sm text-destructive flex items-center gap-1">
            <AlertCircle className="h-3 w-3" />
            {error}
          </p>
        )}
        {!error && helperText && (
          <p id={`${textareaId}-helper`} className="text-sm text-muted-foreground">
            {helperText}
          </p>
        )}
      </div>
    )
  },
)

FormTextarea.displayName = "FormTextarea"
