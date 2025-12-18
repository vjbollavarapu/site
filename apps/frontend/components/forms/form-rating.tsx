"use client"

import * as React from "react"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { Star, AlertCircle } from "lucide-react"

export interface FormRatingProps {
  label?: string
  value?: number
  onChange?: (rating: number) => void
  max?: number
  error?: string
  helperText?: string
  isRequired?: boolean
  disabled?: boolean
  allowHalf?: boolean
  size?: "sm" | "md" | "lg"
  id?: string
}

export const FormRating: React.FC<FormRatingProps> = ({
  label,
  value = 0,
  onChange,
  max = 5,
  error,
  helperText,
  isRequired = false,
  disabled = false,
  allowHalf = false,
  size = "md",
  id,
}) => {
  const [hoverValue, setHoverValue] = React.useState<number | null>(null)
  const ratingId = id || `rating-${label?.toLowerCase().replace(/\s+/g, "-")}`

  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8",
  }

  const handleClick = (rating: number) => {
    if (!disabled) {
      onChange?.(rating)
    }
  }

  const handleMouseEnter = (rating: number) => {
    if (!disabled) {
      setHoverValue(rating)
    }
  }

  const handleMouseLeave = () => {
    setHoverValue(null)
  }

  const getStarValue = (index: number, half: boolean) => {
    return index + (half ? 0.5 : 1)
  }

  const isStarFilled = (starValue: number) => {
    const currentValue = hoverValue !== null ? hoverValue : value
    return currentValue >= starValue
  }

  const isStarHalf = (starValue: number) => {
    const currentValue = hoverValue !== null ? hoverValue : value
    return allowHalf && currentValue >= starValue - 0.5 && currentValue < starValue
  }

  return (
    <div className="space-y-2">
      {label && (
        <Label htmlFor={ratingId} className="text-sm font-medium">
          {label}
          {isRequired && (
            <span className="text-destructive ml-1" aria-label="required">
              *
            </span>
          )}
        </Label>
      )}
      <div
        id={ratingId}
        role="radiogroup"
        aria-required={isRequired}
        aria-invalid={!!error}
        className="flex items-center gap-1"
      >
        {Array.from({ length: max }).map((_, index) => (
          <div key={index} className="relative">
            {allowHalf ? (
              <div className="flex">
                <button
                  type="button"
                  onClick={() => handleClick(getStarValue(index, true))}
                  onMouseEnter={() => handleMouseEnter(getStarValue(index, true))}
                  onMouseLeave={handleMouseLeave}
                  disabled={disabled}
                  className={cn("relative overflow-hidden", disabled ? "cursor-not-allowed" : "cursor-pointer")}
                  style={{ width: "50%" }}
                  aria-label={`Rate ${getStarValue(index, true)} out of ${max}`}
                >
                  <Star
                    className={cn(
                      sizeClasses[size],
                      "transition-colors",
                      isStarFilled(getStarValue(index, true)) || isStarHalf(getStarValue(index, false))
                        ? "fill-yellow-400 text-yellow-400"
                        : "text-muted-foreground",
                    )}
                  />
                </button>
                <button
                  type="button"
                  onClick={() => handleClick(getStarValue(index, false))}
                  onMouseEnter={() => handleMouseEnter(getStarValue(index, false))}
                  onMouseLeave={handleMouseLeave}
                  disabled={disabled}
                  className={cn("relative", disabled ? "cursor-not-allowed" : "cursor-pointer")}
                  style={{ width: "50%" }}
                  aria-label={`Rate ${getStarValue(index, false)} out of ${max}`}
                >
                  <Star
                    className={cn(
                      sizeClasses[size],
                      "transition-colors",
                      isStarFilled(getStarValue(index, false))
                        ? "fill-yellow-400 text-yellow-400"
                        : "text-muted-foreground",
                    )}
                  />
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => handleClick(index + 1)}
                onMouseEnter={() => handleMouseEnter(index + 1)}
                onMouseLeave={handleMouseLeave}
                disabled={disabled}
                className={cn(disabled ? "cursor-not-allowed" : "cursor-pointer")}
                aria-label={`Rate ${index + 1} out of ${max}`}
              >
                <Star
                  className={cn(
                    sizeClasses[size],
                    "transition-colors",
                    isStarFilled(index + 1) ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground",
                  )}
                />
              </button>
            )}
          </div>
        ))}
        {value > 0 && (
          <span className="ml-2 text-sm text-muted-foreground">
            {value.toFixed(allowHalf ? 1 : 0)}/{max}
          </span>
        )}
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
